from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.database import get_db
from app.models.assessment import Assessment
from app.models.subject import Subject
from app.models.user import User
from app.schemas.assessment import AssessmentCreate, AssessmentUpdate, Assessment as AssessmentSchema
from app.schemas.common import PaginatedResponse
from app.api.dependencies import get_current_active_user, get_audit_context
from app.services.audit_service import AuditService
from typing import Dict

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AssessmentSchema])
def get_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    subject_id: Optional[int] = None,
    study_id: Optional[int] = None,
    assessment_type: Optional[str] = None,
    sort_by: Optional[str] = Query(None, regex="^(subject|date)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated list of assessments"""
    query = db.query(Assessment)
    
    if subject_id:
        query = query.filter(Assessment.subject_id == subject_id)
    
    if study_id:
        query = query.filter(Assessment.study_id == study_id)
    
    if assessment_type:
        query = query.filter(Assessment.assessment_type == assessment_type)
    
    # Calculate total before applying joins for sorting
    total = query.count()
    
    # Apply sorting
    if sort_by == "subject":
        # Join with Subject table and sort by last_name, first_name
        query = query.join(Subject, Assessment.subject_id == Subject.id)
        if sort_order == "asc":
            query = query.order_by(Subject.last_name.asc(), Subject.first_name.asc())
        else:
            query = query.order_by(Subject.last_name.desc(), Subject.first_name.desc())
    elif sort_by == "date":
        # Sort by assessment_date
        if sort_order == "asc":
            query = query.order_by(Assessment.assessment_date.asc())
        else:
            query = query.order_by(Assessment.assessment_date.desc())
    else:
        # Default: sort by assessment_date descending
        query = query.order_by(Assessment.assessment_date.desc())
    
    assessments = query.offset(skip).limit(limit).all()
    
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "items": assessments,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/{assessment_id}", response_model=AssessmentSchema)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Get a single assessment by ID"""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Audit log view
    entity_name = f"Assessment {assessment_id} ({assessment.assessment_type})"
    AuditService.log_view(
        db=db,
        user=audit_context['user'],
        entity_type='assessment',
        entity_id=assessment_id,
        entity_name=entity_name,
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )
    
    return assessment


@router.post("", response_model=AssessmentSchema, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_data: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new assessment"""
    db_assessment = Assessment(**assessment_data.model_dump(), created_by=current_user.id)
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.put("/{assessment_id}", response_model=AssessmentSchema)
def update_assessment(
    assessment_id: int,
    assessment_data: AssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an assessment"""
    db_assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not db_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    update_data = assessment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_assessment, field, value)
    
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an assessment"""
    db_assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not db_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    db.delete(db_assessment)
    db.commit()
    return None


@router.get("/types/list", response_model=List[str])
def get_assessment_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of all assessment types"""
    types = db.query(Assessment.assessment_type).distinct().all()
    return [t[0] for t in types]

