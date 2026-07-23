from typing import List, Optional, Dict
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User
from app.models.study import Study
from app.models.user_study import UserStudy
from app.schemas.user import (
    AdminUserCreate,
    AdminUserUpdate,
    User as UserSchema,
)
from app.schemas.study import StudyCreate, StudyUpdate, Study as StudySchema
from app.schemas.user_study_access import UserStudyAccess, UserStudyRoleUpdate
from app.core.security import get_password_hash
from app.api.dependencies import get_current_admin_user, get_audit_context
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter()


# User Management
@router.get("/users", response_model=List[UserSchema])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    query = db.query(User)
    
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    users = query.order_by(User.email).offset(skip).limit(limit).all()
    return users


@router.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context),
    _: User = Depends(get_current_admin_user),
):
    """Create a new user (admin only)"""
    current_user = audit_context['user']
    db_user = db.query(User).filter(User.email == payload.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(payload.password)
    db_user = User(
        email=payload.email,
        hashed_password=hashed_password,
        full_name=payload.full_name,
        location=payload.location,
        phone=payload.phone,
        is_active=True,
        is_superuser=(payload.role == "admin"),
        role=payload.role,
    )
    db.add(db_user)
    db.flush()

    if payload.study_ids:
        studies = db.query(Study).filter(Study.id.in_(payload.study_ids)).all()
        db_user.accessible_studies.extend(studies)

    db.commit()
    db.refresh(db_user)

    AuditService.log_create(
        db=db,
        user=current_user,
        entity_type='user',
        entity_id=db_user.id,
        entity_name=db_user.email,
        entity_data=payload.model_dump(exclude={"password"}),
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )

    return db_user


@router.put("/users/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context),
    _: User = Depends(get_current_admin_user),
):
    """Update user (admin only)"""
    current_user = audit_context['user']
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    changes = {}

    core = payload.model_dump(
        exclude_unset=True,
        exclude={"study_ids", "password", "role"},
    )
    for field, new_value in core.items():
        old_value = getattr(db_user, field, None)
        if old_value != new_value:
            changes[field] = (old_value, new_value)
            setattr(db_user, field, new_value)

    if payload.password and str(payload.password).strip():
        db_user.hashed_password = get_password_hash(str(payload.password).strip())
        changes["password"] = ("[redacted]", "[redacted]")  # never log actual password values

    if "role" in payload.model_fields_set and payload.role is not None:
        if payload.role != db_user.role:
            changes["role"] = (db_user.role, payload.role)
        db_user.role = payload.role
        db_user.is_superuser = payload.role == "admin"

    if "study_ids" in payload.model_fields_set:
        old_study_ids = sorted(s.id for s in db_user.accessible_studies)
        db_user.accessible_studies.clear()
        if payload.study_ids:
            studies = db.query(Study).filter(Study.id.in_(payload.study_ids)).all()
            db_user.accessible_studies.extend(studies)
        new_study_ids = sorted(payload.study_ids or [])
        if old_study_ids != new_study_ids:
            changes["study_ids"] = (old_study_ids, new_study_ids)

    db.commit()
    db.refresh(db_user)

    if changes:
        AuditService.log_update(
            db=db,
            user=current_user,
            entity_type='user',
            entity_id=user_id,
            entity_name=db_user.email,
            changes=changes,
            ip_address=audit_context['ip_address'],
            user_agent=audit_context['user_agent'],
            session_id=audit_context['session_id']
        )

    return db_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context),
    _: User = Depends(get_current_admin_user),
):
    """Delete user (admin only)"""
    current_user = audit_context['user']
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    entity_name = db_user.email
    entity_data = {
        "email": db_user.email,
        "full_name": db_user.full_name,
        "role": db_user.role,
        "is_active": db_user.is_active,
        "is_superuser": db_user.is_superuser,
    }

    db.delete(db_user)
    db.commit()

    AuditService.log_delete(
        db=db,
        user=current_user,
        entity_type='user',
        entity_id=user_id,
        entity_name=entity_name,
        entity_data=entity_data,
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )

    return None


def _user_study_access_list(db: Session, user_id: int) -> List[UserStudyAccess]:
    links = (
        db.query(UserStudy)
        .options(joinedload(UserStudy.study))
        .filter(UserStudy.user_id == user_id)
        .all()
    )
    links.sort(key=lambda row: (row.study.name or "").lower())
    return [
        UserStudyAccess(study=StudySchema.model_validate(row.study), study_role=row.study_role)
        for row in links
    ]


# Study Access Management
@router.get("/users/{user_id}/studies", response_model=List[UserStudyAccess])
def get_user_studies(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
    audit_context: Dict = Depends(get_audit_context),
):
    """Get studies accessible by a user with per-study role (admin only)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    access_rows = _user_study_access_list(db, user_id)

    try:
        AuditService.log_view(
            db=db,
            user=audit_context['user'],
            entity_type='user',
            entity_id=user_id,
            entity_name=f"{db_user.email} - Study Access",
            change_summary=f"Viewed study access for user: {db_user.email}",
            ip_address=audit_context['ip_address'],
            user_agent=audit_context['user_agent'],
            session_id=audit_context['session_id']
        )
    except Exception as exc:
        # Never block study-access UI if audit insert fails (schema drift, DB constraints, etc.).
        logger.warning(
            "get_user_studies audit log skipped user_id=%s: %s",
            user_id,
            exc,
            exc_info=True,
        )

    return access_rows


@router.post("/users/{user_id}/studies", response_model=List[UserStudyAccess])
def add_user_studies(
    user_id: int,
    study_ids: List[int] = Body(...),
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context),
    _: User = Depends(get_current_admin_user),
):
    """Add study access for a user (admin only)"""
    current_user = audit_context['user']
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    studies = db.query(Study).filter(Study.id.in_(study_ids)).all()
    added = [study.name for study in studies if study not in db_user.accessible_studies]
    for study in studies:
        if study not in db_user.accessible_studies:
            db_user.accessible_studies.append(study)

    db.commit()
    db.refresh(db_user)

    if added:
        AuditService.log_action(
            db=db,
            user=current_user,
            action='UPDATE',
            entity_type='user',
            entity_id=user_id,
            entity_name=db_user.email,
            field_name='study_access',
            old_value=None,
            new_value=added,
            change_summary=f"Granted {db_user.email} access to: {', '.join(added)}",
            ip_address=audit_context['ip_address'],
            user_agent=audit_context['user_agent'],
            session_id=audit_context['session_id']
        )

    return _user_study_access_list(db, user_id)


@router.patch("/users/{user_id}/studies/{study_id}", response_model=UserStudyAccess)
def patch_user_study_role(
    user_id: int,
    study_id: int,
    payload: UserStudyRoleUpdate,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context),
    _: User = Depends(get_current_admin_user),
):
    """Update per-study role for a user (admin only)."""
    current_user = audit_context['user']
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    link = (
        db.query(UserStudy)
        .options(joinedload(UserStudy.study))
        .filter(UserStudy.user_id == user_id, UserStudy.study_id == study_id)
        .first()
    )
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study assignment not found",
        )
    old_role = link.study_role
    link.study_role = payload.study_role
    db.commit()
    db.refresh(link)

    if old_role != payload.study_role:
        AuditService.log_action(
            db=db,
            user=current_user,
            action='UPDATE',
            entity_type='user',
            entity_id=user_id,
            entity_name=db_user.email,
            field_name=f'study_role:{link.study.name}',
            old_value=old_role,
            new_value=payload.study_role,
            change_summary=f"Changed {db_user.email}'s role on {link.study.name}: {old_role} -> {payload.study_role}",
            ip_address=audit_context['ip_address'],
            user_agent=audit_context['user_agent'],
            session_id=audit_context['session_id']
        )

    return UserStudyAccess(
        study=StudySchema.model_validate(link.study),
        study_role=link.study_role,
    )


@router.delete("/users/{user_id}/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_study(
    user_id: int,
    study_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context),
    _: User = Depends(get_current_admin_user),
):
    """Remove study access for a user (admin only)"""
    current_user = audit_context['user']
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    study = db.query(Study).filter(Study.id == study_id).first()
    if study and study in db_user.accessible_studies:
        db_user.accessible_studies.remove(study)
        db.commit()

        AuditService.log_action(
            db=db,
            user=current_user,
            action='UPDATE',
            entity_type='user',
            entity_id=user_id,
            entity_name=db_user.email,
            field_name='study_access',
            old_value=study.name,
            new_value=None,
            change_summary=f"Revoked {db_user.email}'s access to: {study.name}",
            ip_address=audit_context['ip_address'],
            user_agent=audit_context['user_agent'],
            session_id=audit_context['session_id']
        )

    return None


