from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.subject_study import subject_study
from app.models.user_study import user_study


class Study(BaseModel):
    __tablename__ = "studies"
    
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String, default="active")  # active, completed, paused
    principal_investigator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    subjects = relationship("Subject", secondary=subject_study, back_populates="studies")
    users = relationship("User", secondary=user_study, back_populates="accessible_studies")
    principal_investigator = relationship("User", foreign_keys=[principal_investigator_id])

