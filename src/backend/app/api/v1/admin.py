from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User
from app.models.study import Study
from app.models.user_study import user_study
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.schemas.study import StudyCreate, StudyUpdate, Study as StudySchema
from app.core.security import get_password_hash
from app.api.dependencies import get_current_admin_user, get_audit_context
from app.services.audit_service import AuditService
from typing import Dict

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
    user_data: UserCreate,
    role: str = Body("viewer"),
    study_ids: Optional[List[int]] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new user (admin only)"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=(role == "admin"),
        role=role
    )
    db.add(db_user)
    db.flush()
    
    # Associate with studies if provided
    if study_ids:
        studies = db.query(Study).filter(Study.id.in_(study_ids)).all()
        db_user.accessible_studies.extend(studies)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/users/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    role: Optional[str] = Body(None),
    study_ids: Optional[List[int]] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user (admin only)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update basic fields
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    # Update role
    if role is not None:
        db_user.role = role
        db_user.is_superuser = (role == "admin")
    
    # Update study access
    if study_ids is not None:
        db_user.accessible_studies.clear()
        if study_ids:
            studies = db.query(Study).filter(Study.id.in_(study_ids)).all()
            db_user.accessible_studies.extend(studies)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user (admin only)"""
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
    
    db.delete(db_user)
    db.commit()
    return None


# Study Access Management
@router.get("/users/{user_id}/studies", response_model=List[StudySchema])
def get_user_studies(
    user_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Get studies accessible by a user (admin only)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Audit log view (viewing user's study access is sensitive)
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
    
    return db_user.accessible_studies


@router.post("/users/{user_id}/studies", response_model=List[StudySchema])
def add_user_studies(
    user_id: int,
    study_ids: List[int] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Add study access for a user (admin only)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    studies = db.query(Study).filter(Study.id.in_(study_ids)).all()
    for study in studies:
        if study not in db_user.accessible_studies:
            db_user.accessible_studies.append(study)
    
    db.commit()
    db.refresh(db_user)
    return db_user.accessible_studies


@router.delete("/users/{user_id}/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_study(
    user_id: int,
    study_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Remove study access for a user (admin only)"""
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
    
    return None


