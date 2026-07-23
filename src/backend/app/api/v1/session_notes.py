from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.session_note import SessionNote
from app.models.subject import Subject
from app.models.user import User
from app.schemas.session_note import SessionNoteCreate, SessionNoteUpdate, SessionNote as SessionNoteSchema
from app.schemas.common import PaginatedResponse
from app.api.dependencies import (
    get_current_active_user,
    get_current_researcher_user,
    check_study_access,
    require_study_access,
    require_study_write_access,
    get_audit_context,
)
from app.services.audit_service import AuditService
from typing import Dict

router = APIRouter()


@router.get("", response_model=PaginatedResponse[SessionNoteSchema])
def get_session_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    subject_id: Optional[int] = None,
    study_id: Optional[int] = None,
    sort_by: Optional[str] = Query(None, regex="^(subject|date)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated list of session notes"""
    query = db.query(SessionNote)

    if subject_id:
        query = query.filter(SessionNote.subject_id == subject_id)

    if study_id:
        require_study_access(study_id, current_user, db)
        query = query.filter(SessionNote.study_id == study_id)
    elif not (current_user.is_superuser or current_user.role == "admin"):
        # Non-admins only see session notes from their accessible studies
        accessible_study_ids = [s.id for s in current_user.accessible_studies]
        if accessible_study_ids:
            query = query.filter(SessionNote.study_id.in_(accessible_study_ids))
        else:
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
    if sort_by == "subject":
        # Join with Subject table and sort by last_name, first_name
        query = query.join(Subject, SessionNote.subject_id == Subject.id)
        if sort_order == "asc":
            query = query.order_by(Subject.last_name.asc(), Subject.first_name.asc())
        else:
            query = query.order_by(Subject.last_name.desc(), Subject.first_name.desc())
    elif sort_by == "date":
        if sort_order == "asc":
            query = query.order_by(SessionNote.session_date.asc())
        else:
            query = query.order_by(SessionNote.session_date.desc())
    else:
        # Default: sort by session_date descending
        query = query.order_by(SessionNote.session_date.desc())
    
    notes = query.offset(skip).limit(limit).all()
    
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "items": notes,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/{note_id}", response_model=SessionNoteSchema)
def get_session_note(
    note_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context)
):
    """Get a single session note by ID"""
    note = db.query(SessionNote).filter(SessionNote.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )

    current_user = audit_context['user']
    if not (current_user.is_superuser or current_user.role == "admin"):
        if note.study_id is None or not check_study_access(note.study_id, current_user, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this session note's study"
            )

    # Audit log view
    from datetime import datetime
    entity_name = f"Session Note {note_id} ({note.session_date.strftime('%Y-%m-%d') if note.session_date else 'No date'})"
    AuditService.log_view(
        db=db,
        user=audit_context['user'],
        entity_type='session_note',
        entity_id=note_id,
        entity_name=entity_name,
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )
    
    return note


def _session_note_entity_name(note) -> str:
    return f"Session Note {note.id} ({note.session_date.strftime('%Y-%m-%d') if note.session_date else 'No date'})"


@router.post("", response_model=SessionNoteSchema, status_code=status.HTTP_201_CREATED)
def create_session_note(
    note_data: SessionNoteCreate,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context),
    _: User = Depends(get_current_researcher_user),
):
    """Create a new session note"""
    current_user = audit_context['user']
    require_study_write_access(note_data.study_id, current_user, db)
    db_note = SessionNote(**note_data.model_dump(), created_by=current_user.id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    AuditService.log_create(
        db=db,
        user=current_user,
        entity_type='session_note',
        entity_id=db_note.id,
        entity_name=_session_note_entity_name(db_note),
        entity_data=note_data.model_dump(),
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )

    return db_note


@router.put("/{note_id}", response_model=SessionNoteSchema)
def update_session_note(
    note_id: int,
    note_data: SessionNoteUpdate,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context),
    _: User = Depends(get_current_researcher_user),
):
    """Update a session note"""
    current_user = audit_context['user']
    db_note = db.query(SessionNote).filter(SessionNote.id == note_id).first()
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )

    require_study_write_access(db_note.study_id, current_user, db)

    changes = {}
    update_data = note_data.model_dump(exclude_unset=True)
    for field, new_value in update_data.items():
        old_value = getattr(db_note, field, None)
        if old_value != new_value:
            changes[field] = (old_value, new_value)
            setattr(db_note, field, new_value)

    db.commit()
    db.refresh(db_note)

    if changes:
        AuditService.log_update(
            db=db,
            user=current_user,
            entity_type='session_note',
            entity_id=note_id,
            entity_name=_session_note_entity_name(db_note),
            changes=changes,
            ip_address=audit_context['ip_address'],
            user_agent=audit_context['user_agent'],
            session_id=audit_context['session_id']
        )

    return db_note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session_note(
    note_id: int,
    db: Session = Depends(get_db),
    audit_context: Dict = Depends(get_audit_context),
    _: User = Depends(get_current_researcher_user),
):
    """Delete a session note"""
    current_user = audit_context['user']
    db_note = db.query(SessionNote).filter(SessionNote.id == note_id).first()
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )

    require_study_write_access(db_note.study_id, current_user, db)

    entity_name = _session_note_entity_name(db_note)
    entity_data = {
        'subject_id': db_note.subject_id,
        'study_id': db_note.study_id,
        'session_date': db_note.session_date.isoformat() if db_note.session_date else None,
        'notes': db_note.notes,
        'created_by': db_note.created_by,
    }

    db.delete(db_note)
    db.commit()

    AuditService.log_delete(
        db=db,
        user=current_user,
        entity_type='session_note',
        entity_id=note_id,
        entity_name=entity_name,
        entity_data=entity_data,
        ip_address=audit_context['ip_address'],
        user_agent=audit_context['user_agent'],
        session_id=audit_context['session_id']
    )

    return None

