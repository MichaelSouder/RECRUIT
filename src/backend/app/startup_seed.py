"""Optional first-boot seed for production-style deployments."""
import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import get_password_hash
from app.database import SessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)


def seed_initial_admin_if_configured() -> None:
    """
    When SEED_INITIAL_ADMIN is true and INITIAL_ADMIN_PASSWORD is set, create exactly one
    admin user if the database has no users. Otherwise no-op.
    """
    if not settings.seed_initial_admin:
        return

    pwd = (settings.initial_admin_password or "").strip()
    if not pwd:
        logger.warning(
            "SEED_INITIAL_ADMIN is enabled but INITIAL_ADMIN_PASSWORD is empty; "
            "skipping initial admin creation."
        )
        return

    db: Session = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return

        email = settings.initial_admin_email.strip().lower()
        user = User(
            email=email,
            hashed_password=get_password_hash(pwd),
            full_name="Administrator",
            is_active=True,
            is_superuser=True,
            role="admin",
        )
        db.add(user)
        db.commit()
        logger.info("Created initial admin user for empty database (email=%s).", email)
    except Exception:
        logger.exception("Failed to seed initial admin user.")
        db.rollback()
    finally:
        db.close()
