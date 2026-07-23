from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime


class AssessmentTypeBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    min_score: Optional[str] = None
    max_score: Optional[str] = None
    fields: Optional[Any] = None
    is_active: Optional[str] = "true"


class AssessmentTypeCreate(AssessmentTypeBase):
    pass


class AssessmentTypeUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    min_score: Optional[str] = None
    max_score: Optional[str] = None
    fields: Optional[Any] = None
    is_active: Optional[str] = None


class AssessmentType(AssessmentTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


