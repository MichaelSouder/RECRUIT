from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import List, Optional


def lowercase_email(v: Optional[str]) -> Optional[str]:
    """Lowercase/strip so DB lookups (User.email == ...) stay case-insensitive-in-practice."""
    if v is None:
        return v
    return v.lower().strip()


class UserBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    email: EmailStr
    full_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return lowercase_email(v)


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, str_strip_whitespace=True)

    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return lowercase_email(v)


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class AdminUserCreate(BaseModel):
    """Single JSON body for admin create-user (avoids multiple FastAPI Body parameters)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str
    full_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    role: str = "viewer"
    study_ids: Optional[List[int]] = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return lowercase_email(v)


class AdminUserUpdate(BaseModel):
    """Single JSON body for admin update-user."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    study_ids: Optional[List[int]] = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        return lowercase_email(v)


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    role: Optional[str] = "viewer"
    piv_certificate_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
