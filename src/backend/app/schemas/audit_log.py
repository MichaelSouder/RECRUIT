from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AuditLogBase(BaseModel):
    timestamp: datetime
    user_id: int
    user_email: str
    user_full_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: int
    entity_name: Optional[str] = None
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_summary: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    additional_context: Optional[str] = None


class AuditLog(AuditLogBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogCreate(AuditLogBase):
    pass





