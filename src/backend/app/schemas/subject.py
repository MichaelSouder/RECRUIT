from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class SubjectBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    ssn: Optional[str] = None
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    death_date: Optional[date] = None
    county: Optional[str] = None
    zip: Optional[str] = None
    enrollment_status: Optional[str] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    ssn: Optional[str] = None
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    death_date: Optional[date] = None
    county: Optional[str] = None
    zip: Optional[str] = None
    enrollment_status: Optional[str] = None


class Subject(SubjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

