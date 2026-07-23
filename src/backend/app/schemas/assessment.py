from pydantic import BaseModel, ConfigDict
from typing import Any, Optional
from datetime import date, datetime, time


class AssessmentBase(BaseModel):
    subject_id: int
    study_id: Optional[int] = None
    assessment_type: str
    assessment_date: date
    assessment_time: Optional[time] = None
    total_score: Optional[float] = None
    notes: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentUpdate(BaseModel):
    study_id: Optional[int] = None
    assessment_type: Optional[str] = None
    assessment_date: Optional[date] = None
    assessment_time: Optional[time] = None
    total_score: Optional[float] = None
    notes: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class Assessment(AssessmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

