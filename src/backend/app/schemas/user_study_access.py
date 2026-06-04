from pydantic import BaseModel, Field

from app.schemas.study import Study as StudySchema


class UserStudyAccess(BaseModel):
    study: StudySchema
    study_role: str = Field(..., pattern="^(admin|researcher|viewer)$")

    class Config:
        from_attributes = True


class UserStudyRoleUpdate(BaseModel):
    study_role: str = Field(..., pattern="^(admin|researcher|viewer)$")
