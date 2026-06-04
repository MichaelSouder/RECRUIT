from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class UserStudy(Base):
    """Association between users and studies, including per-study role."""

    __tablename__ = "user_study"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    study_id = Column(Integer, ForeignKey("studies.id"), primary_key=True)
    study_role = Column(String, nullable=False, default="viewer")

    user = relationship("User", back_populates="study_memberships")
    study = relationship("Study", back_populates="user_study_links")
