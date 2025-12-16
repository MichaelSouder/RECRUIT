from sqlalchemy import Column, String, Text, JSON
from app.models.base import BaseModel


class AssessmentType(BaseModel):
    """Dynamic assessment type definitions"""
    __tablename__ = "assessment_types"
    
    name = Column(String, nullable=False, unique=True)  # e.g., 'moca', 'dass21'
    display_name = Column(String, nullable=False)  # e.g., 'MoCA', 'DASS-21'
    description = Column(Text, nullable=True)
    min_score = Column(String, nullable=True)  # JSON string for flexibility
    max_score = Column(String, nullable=True)
    fields = Column(JSON, nullable=True)  # Dynamic field definitions
    is_active = Column(String, default="true")  # String to match SQLite compatibility


