from sqlalchemy import Column, String, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.subject_study import subject_study


class Subject(BaseModel):
    __tablename__ = "subjects"
    
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    sex = Column(String, nullable=True)  # 'male' or 'female'
    ssn = Column(String, nullable=True)  # Should be encrypted in production
    race = Column(String, nullable=True)  # FDA-required race categories
    ethnicity = Column(String, nullable=True)  # FDA-required ethnicity categories
    death_date = Column(Date, nullable=True)
    county = Column(String, nullable=True)
    zip = Column(String, nullable=True)
    enrollment_status = Column(String, nullable=True, default="not_enrolled")  # 'enrolled', 'not_enrolled'
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    studies = relationship("Study", secondary=subject_study, back_populates="subjects")

