from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.assessment_type import AssessmentType
from app.models.user import User
from app.schemas.assessment_type import (
    AssessmentTypeCreate,
    AssessmentTypeUpdate,
    AssessmentType as AssessmentTypeSchema
)
from app.api.dependencies import get_current_active_user, get_current_admin_user, get_audit_context
from app.services.audit_service import AuditService
from typing import Dict

router = APIRouter()


@router.get("", response_model=List[AssessmentTypeSchema])
def get_assessment_types(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all assessment types"""
    query = db.query(AssessmentType)
    if active_only:
        query = query.filter(AssessmentType.is_active == "true")
    return query.order_by(AssessmentType.display_name).all()


@router.get("/{type_id}", response_model=AssessmentTypeSchema)
def get_assessment_type(
    type_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Get assessment type by ID"""
    assessment_type = db.query(AssessmentType).filter(AssessmentType.id == type_id).first()
    if not assessment_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment type not found"
        )
    
    # Audit log view
    AuditService.log_view(
        db=db,
        user=audit_context['user'],
        entity_type='assessment_type',
        entity_id=type_id,
        entity_name=assessment_type.display_name,
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )
    
    return assessment_type


@router.post("", response_model=AssessmentTypeSchema, status_code=status.HTTP_201_CREATED)
def create_assessment_type(
    assessment_type_data: AssessmentTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new assessment type (admin only)"""
    # Check if name already exists
    existing = db.query(AssessmentType).filter(AssessmentType.name == assessment_type_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment type with this name already exists"
        )
    
    db_assessment_type = AssessmentType(**assessment_type_data.model_dump())
    db.add(db_assessment_type)
    db.commit()
    db.refresh(db_assessment_type)
    return db_assessment_type


@router.put("/{type_id}", response_model=AssessmentTypeSchema)
def update_assessment_type(
    type_id: int,
    assessment_type_data: AssessmentTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update assessment type (admin only)"""
    db_assessment_type = db.query(AssessmentType).filter(AssessmentType.id == type_id).first()
    if not db_assessment_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment type not found"
        )
    
    update_data = assessment_type_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_assessment_type, field, value)
    
    db.commit()
    db.refresh(db_assessment_type)
    return db_assessment_type


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete assessment type (admin only)"""
    db_assessment_type = db.query(AssessmentType).filter(AssessmentType.id == type_id).first()
    if not db_assessment_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment type not found"
        )
    
    # Soft delete by setting is_active to false
    db_assessment_type.is_active = "false"
    db.commit()
    return None


