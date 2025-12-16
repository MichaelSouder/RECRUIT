from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base


class AuditLog(Base):
    """Audit log model for FDA 21 CFR Part 11 compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # User information (denormalized for historical accuracy)
    user_id = Column(Integer, nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_full_name = Column(String(255), nullable=True)
    
    # Action details
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, VIEW, EXPORT, LOGIN, LOGOUT
    entity_type = Column(String(100), nullable=False, index=True)  # 'subject', 'study', 'assessment', etc.
    entity_id = Column(Integer, nullable=False, index=True)
    entity_name = Column(String(255), nullable=True)  # Human-readable identifier
    
    # Field-level changes (for UPDATE actions)
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)  # JSON string for complex data
    new_value = Column(Text, nullable=True)  # JSON string for complex data
    
    # Summary
    change_summary = Column(Text, nullable=True)
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Additional metadata
    additional_context = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Composite index for entity queries
    __table_args__ = (
        Index('idx_audit_logs_entity', 'entity_type', 'entity_id'),
    )





