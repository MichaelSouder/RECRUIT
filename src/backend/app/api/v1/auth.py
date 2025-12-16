from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, User as UserSchema, UserUpdate
from app.schemas.profile import ProfileUpdate, PasswordChange
from app.schemas.common import Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.dependencies import get_current_active_user, get_audit_context
from app.services.audit_service import AuditService
from fastapi import Request
from typing import Dict, Optional
from app.config import settings
from pydantic import BaseModel

router = APIRouter()


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Email is already lowercased by the validator
    logger.info(f"Login attempt for email: {user_data.email}")
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        logger.warning(f"User not found: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"User found: {user.email}, is_active: {user.is_active}")
    password_valid = verify_password(user_data.password, user.hashed_password)
    logger.info(f"Password verification result: {password_valid}")
    
    if not password_valid:
        logger.warning(f"Password verification failed for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    # Audit log login
    ip_address = getattr(request.state, 'ip_address', None) if hasattr(request, 'state') else None
    user_agent = getattr(request.state, 'user_agent', None) if hasattr(request, 'state') else None
    session_id = getattr(request.state, 'session_id', None) if hasattr(request, 'state') else None
    
    AuditService.log_login(
        db=db,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


class PIVLoginRequest(BaseModel):
    certificate_id: str  # Certificate identifier (CN, SAN, or serial number)


@router.post("/login-piv", response_model=Token)
def login_piv(
    piv_data: PIVLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login using PIV certificate"""
    # Find user by PIV certificate ID
    user = db.query(User).filter(User.piv_certificate_id == piv_data.certificate_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIV certificate not registered",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    # Audit log login
    ip_address = getattr(request.state, 'ip_address', None) if hasattr(request, 'state') else None
    user_agent = getattr(request.state, 'user_agent', None) if hasattr(request, 'state') else None
    session_id = getattr(request.state, 'session_id', None) if hasattr(request, 'state') else None
    
    AuditService.log_login(
        db=db,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserSchema)
def update_current_user_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information"""
    update_data = profile_update.model_dump(exclude_unset=True)
    
    # Check if email is being changed and if it's already taken
    if "email" in update_data and update_data["email"] != current_user.email:
        existing_user = db.query(User).filter(User.email == update_data["email"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    return None

