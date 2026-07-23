from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.security import decode_access_token
from typing import Optional, Dict

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    # Convert string back to int for database query
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current admin user"""
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_researcher_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current researcher or admin user"""
    if current_user.role not in ["admin", "researcher"] and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def check_study_access(study_id: Optional[int], current_user: User, db: Session) -> bool:
    """Check if user has access to a study"""
    # Admins and superusers have access to all studies
    if current_user.is_superuser or current_user.role == "admin":
        return True

    # If no study_id, allow (will be filtered by accessible studies)
    if study_id is None:
        return True

    # Refresh memberships so study access reflects latest assignments
    db.refresh(current_user, ["study_memberships"])

    accessible_study_ids = [m.study_id for m in current_user.study_memberships]
    return study_id in accessible_study_ids


def require_study_access(study_id: Optional[int], current_user: User, db: Session):
    """Require that user has access to a study"""
    if not check_study_access(study_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this study"
        )


def _get_study_membership(study_id: int, current_user: User, db: Session):
    """Return the UserStudy membership row for current_user in study_id, or None."""
    db.refresh(current_user, ["study_memberships"])
    return next((m for m in current_user.study_memberships if m.study_id == study_id), None)


def check_study_write_access(study_id: Optional[int], current_user: User, db: Session) -> bool:
    """Check if user can write data within a study (create/edit subjects, assessments, notes).

    Requires global researcher role + study_role of researcher or admin for the study.
    Global admins/superusers always pass.
    """
    if current_user.is_superuser or current_user.role == "admin":
        return True
    if current_user.role != "researcher":
        return False
    if study_id is None:
        return True
    membership = _get_study_membership(study_id, current_user, db)
    if membership is None:
        return False
    return membership.study_role in ("researcher", "admin")


def require_study_write_access(study_id: Optional[int], current_user: User, db: Session):
    """Require write access to a study; raise 403 otherwise."""
    if not check_study_write_access(study_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have write access to this study"
        )


def check_study_manage_access(study_id: int, current_user: User, db: Session) -> bool:
    """Check if user can manage a study's own metadata (update/delete the study record).

    Requires global admin, OR global researcher with study_role='admin' for that study.
    """
    if current_user.is_superuser or current_user.role == "admin":
        return True
    if current_user.role != "researcher":
        return False
    membership = _get_study_membership(study_id, current_user, db)
    if membership is None:
        return False
    return membership.study_role == "admin"


def require_study_manage_access(study_id: int, current_user: User, db: Session):
    """Require study-management access; raise 403 otherwise."""
    if not check_study_manage_access(study_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage this study"
        )


def get_audit_context(
    request: Request,
    current_user: User = Depends(get_current_active_user)
) -> Dict:
    """Get audit context from request for audit logging"""
    return {
        'ip_address': getattr(request.state, 'ip_address', None),
        'user_agent': getattr(request.state, 'user_agent', None),
        'session_id': getattr(request.state, 'session_id', None),
        'user': current_user
    }
