from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.study import Study
from app.models.user import User
from app.schemas.study import StudyCreate, StudyUpdate, Study as StudySchema
from app.schemas.common import PaginatedResponse
from app.api.dependencies import get_current_active_user, require_study_access, get_audit_context
from app.services.audit_service import AuditService
from typing import Dict

router = APIRouter()


@router.get("/researchers", response_model=List[dict])
def get_researchers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of researchers (for PI dropdown)"""
    researchers = db.query(User).filter(
        User.role.in_(["researcher", "admin"]),
        User.is_active == True
    ).order_by(User.full_name, User.email).all()
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name or user.email,
            "role": user.role
        }
        for user in researchers
    ]


@router.get("", response_model=PaginatedResponse[StudySchema])
def get_studies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: Optional[str] = Query(None, regex="^(name|status|start_date)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated list of studies"""
    query = db.query(Study)
    
    # Non-admins only see studies they have access to
    if not (current_user.is_superuser or current_user.role == "admin"):
        accessible_study_ids = [s.id for s in current_user.accessible_studies]
        if accessible_study_ids:
            query = query.filter(Study.id.in_(accessible_study_ids))
        else:
            # No accessible studies, return empty
            return {
                "items": [],
                "total": 0,
                "page": 1,
                "size": limit,
                "pages": 0
            }
    
    # Calculate total before applying sorting
    total = query.count()
    
    # Apply sorting
    if sort_by == "name":
        if sort_order == "asc":
            query = query.order_by(Study.name.asc())
        else:
            query = query.order_by(Study.name.desc())
    elif sort_by == "status":
        if sort_order == "asc":
            query = query.order_by(Study.status.asc())
        else:
            query = query.order_by(Study.status.desc())
    elif sort_by == "start_date":
        if sort_order == "asc":
            query = query.order_by(Study.start_date.asc().nulls_last())
        else:
            query = query.order_by(Study.start_date.desc().nulls_last())
    else:
        # Default: sort by name ascending
        query = query.order_by(Study.name.asc())
    
    studies = query.offset(skip).limit(limit).all()
    
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "items": studies,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/{study_id}", response_model=StudySchema)
def get_study(
    study_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Get a single study by ID"""
    study = db.query(Study).filter(Study.id == study_id).first()
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study not found"
        )
    
    # Check if user has access to this study
    require_study_access(study_id, audit_context['user'], db)
    
    # Audit log view
    AuditService.log_view(
        db=db,
        user=audit_context['user'],
        entity_type='study',
        entity_id=study_id,
        entity_name=study.name,
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )
    
    return study


@router.post("", response_model=StudySchema, status_code=status.HTTP_201_CREATED)
def create_study(
    study_data: StudyCreate,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Create a new study"""
    # Check if study name already exists
    existing = db.query(Study).filter(Study.name == study_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Study with this name already exists"
        )
    
    db_study = Study(**study_data.model_dump())
    db.add(db_study)
    db.commit()
    db.refresh(db_study)
    
    # Audit log
    AuditService.log_create(
        db=db,
        user=audit_context['user'],
        entity_type='study',
        entity_id=db_study.id,
        entity_name=db_study.name,
        entity_data=study_data.model_dump(),
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )
    
    return db_study


@router.put("/{study_id}", response_model=StudySchema)
def update_study(
    study_id: int,
    study_data: StudyUpdate,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Update a study"""
    db_study = db.query(Study).filter(Study.id == study_id).first()
    if not db_study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study not found"
        )
    
    # Check name uniqueness if name is being updated
    if study_data.name and study_data.name != db_study.name:
        existing = db.query(Study).filter(Study.name == study_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Study with this name already exists"
            )
    
    # Track changes
    changes = {}
    update_data = study_data.model_dump(exclude_unset=True)
    for field, new_value in update_data.items():
        old_value = getattr(db_study, field, None)
        if old_value != new_value:
            changes[field] = (old_value, new_value)
            setattr(db_study, field, new_value)
    
    db.commit()
    db.refresh(db_study)
    
    # Audit log
    if changes:
        AuditService.log_update(
            db=db,
            user=audit_context['user'],
            entity_type='study',
            entity_id=study_id,
            entity_name=db_study.name,
            changes=changes,
            ip_address=audit_context['ip_address'],
            user_agent=audit_context['user_agent'],
            session_id=audit_context['session_id']
        )
    
    return db_study


@router.delete("/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study(
    study_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Delete a study"""
    db_study = db.query(Study).filter(Study.id == study_id).first()
    if not db_study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study not found"
        )
    
    # Capture entity data before deletion
    entity_data = {
        'name': db_study.name,
        'description': db_study.description,
        'start_date': db_study.start_date.isoformat() if db_study.start_date else None,
        'end_date': db_study.end_date.isoformat() if db_study.end_date else None,
        'status': db_study.status,
        'principal_investigator_id': db_study.principal_investigator_id
    }
    
    db.delete(db_study)
    db.commit()
    
    # Audit log
    AuditService.log_delete(
        db=db,
        user=audit_context['user'],
        entity_type='study',
        entity_id=study_id,
        entity_name=db_study.name,
        entity_data=entity_data,
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )
    
    return None

