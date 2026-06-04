from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.user_study import UserStudy


class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    piv_certificate_id = Column(String, nullable=True, unique=True, index=True)  # PIV certificate identifier (CN or SAN)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default="viewer")  # admin, researcher, viewer
    
    study_memberships = relationship(
        "UserStudy",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    accessible_studies = association_proxy(
        "study_memberships",
        "study",
        creator=lambda study: UserStudy(study=study, study_role="viewer"),
    )

