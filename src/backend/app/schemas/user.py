from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
import re


class UserBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email: str
    full_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email"""
        if isinstance(v, str):
            # Check basic email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
            return v.lower().strip()
        return v


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, str_strip_whitespace=True)
    
    email: str
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email"""
        if isinstance(v, str):
            # Check basic email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
            return v.lower().strip()
        return v


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    role: Optional[str] = "viewer"
    piv_certificate_id: Optional[str] = None
    
    class Config:
        from_attributes = True

