from sqlalchemy import Column, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class StudyProcedure(BaseModel):
    """Arc ``studyproc_list`` matrix: allowed procedure codes per RECRUIT study."""

    __tablename__ = "study_procedures"
    __table_args__ = (UniqueConstraint("study_id", "proc_code", name="uq_study_procedures_study_proc"),)

    study_id = Column(Integer, ForeignKey("studies.id"), nullable=False, index=True)
    proc_code = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=True)
    legacy_index = Column(Integer, nullable=True)
    data = Column(JSON, nullable=True)

    study = relationship("Study", back_populates="study_procedures")
