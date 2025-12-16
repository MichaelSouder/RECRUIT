from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class SessionNoteBase(BaseModel):
    subject_id: int
    study_id: Optional[int] = None
    session_date: date
    notes: Optional[str] = None


class SessionNoteCreate(SessionNoteBase):
    pass


class SessionNoteUpdate(BaseModel):
    study_id: Optional[int] = None
    session_date: Optional[date] = None
    notes: Optional[str] = None


class SessionNote(SessionNoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

