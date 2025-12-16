from sqlalchemy import Column, String, Date, Time, Integer, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Assessment(BaseModel):
    """Base assessment model - can be extended for specific assessment types"""
    __tablename__ = "assessments"
    
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    study_id = Column(Integer, ForeignKey("studies.id"), nullable=True)
    assessment_type = Column(String, nullable=False)  # References assessment_types.name
    assessment_date = Column(Date, nullable=False)
    assessment_time = Column(Time, nullable=True)
    total_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)  # Flexible JSON field for assessment-specific data
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    subject = relationship("Subject", foreign_keys=[subject_id])
    study = relationship("Study", foreign_keys=[study_id])
    creator = relationship("User", foreign_keys=[created_by])

