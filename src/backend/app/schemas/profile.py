from pydantic import BaseModel, field_validator
from typing import Optional
import re


class ProfileUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if v is None:
            return v
        # Allow test domains for development
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


