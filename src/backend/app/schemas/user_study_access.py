from pydantic import BaseModel, ConfigDict, Field

from app.schemas.study import Study as StudySchema


class UserStudyAccess(BaseModel):
    study: StudySchema
    study_role: str = Field(..., pattern="^(admin|researcher|viewer)$")

    model_config = ConfigDict(from_attributes=True)


class UserStudyRoleUpdate(BaseModel):
    study_role: str = Field(..., pattern="^(admin|researcher|viewer)$")
