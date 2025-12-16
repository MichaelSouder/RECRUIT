from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SessionNote(BaseModel):
    __tablename__ = "session_notes"
    
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    study_id = Column(Integer, ForeignKey("studies.id"), nullable=True)
    session_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    subject = relationship("Subject", foreign_keys=[subject_id])
    study = relationship("Study", foreign_keys=[study_id])
    creator = relationship("User", foreign_keys=[created_by])

