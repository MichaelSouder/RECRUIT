from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class StudyBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "active"
    principal_investigator_id: Optional[int] = None


class StudyCreate(StudyBase):
    pass


class StudyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    principal_investigator_id: Optional[int] = None


class Study(StudyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

