from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.user_study import user_study


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
    
    # Relationships
    accessible_studies = relationship("Study", secondary=user_study, back_populates="users")

