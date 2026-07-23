from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

from app.schemas.user import lowercase_email


class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        return lowercase_email(v)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
