from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.study import Study
from app.database import get_db
from app.models.subject import Subject
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectUpdate, Subject as SubjectSchema
from app.schemas.common import PaginatedResponse
from app.api.dependencies import get_current_active_user, require_study_access, get_audit_context
from app.services.audit_service import AuditService
from typing import Dict

router = APIRouter()


@router.get("", response_model=PaginatedResponse[SubjectSchema])
def get_subjects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    study_id: Optional[int] = None,
    sort_by: Optional[str] = Query(None, regex="^(name|dob|sex|race)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated list of subjects"""
    query = db.query(Subject)
    
    # Filter by study and check access
    if study_id:
        require_study_access(study_id, current_user, db)
        query = query.join(Subject.studies).filter_by(id=study_id)
    elif not (current_user.is_superuser or current_user.role == "admin"):
        # Non-admins only see subjects from their accessible studies
        accessible_study_ids = [s.id for s in current_user.accessible_studies]
        if accessible_study_ids:
            query = query.join(Subject.studies).filter(Study.id.in_(accessible_study_ids))
        else:
            # No accessible studies, return empty
            return {
                "items": [],
                "total": 0,
                "page": 1,
                "size": limit,
                "pages": 0
            }
    
    # Search functionality
    if search:
        search_filter = or_(
            Subject.first_name.ilike(f"%{search}%"),
            Subject.last_name.ilike(f"%{search}%"),
            Subject.middle_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Calculate total before applying sorting
    total = query.count()
    
    # Apply sorting
    if sort_by == "name":
        if sort_order == "asc":
            query = query.order_by(Subject.last_name.asc(), Subject.first_name.asc())
        else:
            query = query.order_by(Subject.last_name.desc(), Subject.first_name.desc())
    elif sort_by == "dob":
        if sort_order == "asc":
            query = query.order_by(Subject.date_of_birth.asc().nulls_last())
        else:
            query = query.order_by(Subject.date_of_birth.desc().nulls_last())
    elif sort_by == "sex":
        if sort_order == "asc":
            query = query.order_by(Subject.sex.asc().nulls_last())
        else:
            query = query.order_by(Subject.sex.desc().nulls_last())
    elif sort_by == "race":
        if sort_order == "asc":
            query = query.order_by(Subject.race.asc().nulls_last())
        else:
            query = query.order_by(Subject.race.desc().nulls_last())
    else:
        # Default: sort by name ascending
        query = query.order_by(Subject.last_name.asc(), Subject.first_name.asc())
    
    subjects = query.offset(skip).limit(limit).all()
    
    # Calculate pages
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "items": subjects,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/{subject_id}", response_model=SubjectSchema)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Get a single subject by ID"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Audit log view
    entity_name = f"{subject.last_name}, {subject.first_name}"
    AuditService.log_view(
        db=db,
        user=audit_context['user'],
        entity_type='subject',
        entity_id=subject_id,
        entity_name=entity_name,
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )
    
    return subject


@router.post("", response_model=SubjectSchema, status_code=status.HTTP_201_CREATED)
def create_subject(
    request_data: dict = Body(...),
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Create a new subject"""
    from app.models.study import Study
    
    # Extract study_ids if present
    study_ids = request_data.pop('study_ids', None)
    
    # Create subject from remaining data
    subject_data = SubjectCreate(**request_data)
    db_subject = Subject(**subject_data.model_dump(), created_by=audit_context['user'].id)
    db.add(db_subject)
    db.flush()  # Get the ID
    
    # Associate with studies if provided
    if study_ids:
        studies = db.query(Study).filter(Study.id.in_(study_ids)).all()
        db_subject.studies.extend(studies)
    
    db.commit()
    db.refresh(db_subject)
    
    # Audit log
    entity_name = f"{db_subject.last_name}, {db_subject.first_name}"
    AuditService.log_create(
        db=db,
        user=audit_context['user'],
        entity_type='subject',
        entity_id=db_subject.id,
        entity_name=entity_name,
        entity_data=subject_data.model_dump(),
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )
    
    return db_subject


@router.put("/{subject_id}", response_model=SubjectSchema)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Update a subject"""
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Track changes
    changes = {}
    update_data = subject_data.model_dump(exclude_unset=True)
    for field, new_value in update_data.items():
        old_value = getattr(db_subject, field, None)
        if old_value != new_value:
            changes[field] = (old_value, new_value)
            setattr(db_subject, field, new_value)
    
    db.commit()
    db.refresh(db_subject)
    
    # Audit log
    if changes:
        entity_name = f"{db_subject.last_name}, {db_subject.first_name}"
        AuditService.log_update(
            db=db,
            user=audit_context['user'],
            entity_type='subject',
            entity_id=subject_id,
            entity_name=entity_name,
            changes=changes,
            ip_address=audit_context['ip_address'],
            user_agent=audit_context['user_agent'],
            session_id=audit_context['session_id']
        )
    
    return db_subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Delete a subject"""
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Capture entity data before deletion
    entity_name = f"{db_subject.last_name}, {db_subject.first_name}"
    entity_data = {
        'first_name': db_subject.first_name,
        'last_name': db_subject.last_name,
        'middle_name': db_subject.middle_name,
        'date_of_birth': db_subject.date_of_birth.isoformat() if db_subject.date_of_birth else None,
        'gender': db_subject.gender,
        'created_by': db_subject.created_by
    }
    
    db.delete(db_subject)
    db.commit()
    
    # Audit log
    AuditService.log_delete(
        db=db,
        user=audit_context['user'],
        entity_type='subject',
        entity_id=subject_id,
        entity_name=entity_name,
        entity_data=entity_data,
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )
    
    return None

