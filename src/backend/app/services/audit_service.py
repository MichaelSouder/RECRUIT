from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.user import User
from typing import Optional, Dict, Any
import json


class AuditService:
    """Service for creating FDA-compliant audit trail entries"""
    
    @staticmethod
    def _serialize_value(value: Any) -> Optional[str]:
        """Serialize a value to JSON string"""
        if value is None:
            return None
        try:
            # Handle datetime objects
            if isinstance(value, datetime):
                return value.isoformat()
            # Handle dict/list - convert to JSON
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            # Handle other types - convert to string then JSON
            return json.dumps(str(value))
        except (TypeError, ValueError):
            # Fallback to string representation
            return str(value)
    
    @staticmethod
    def log_action(
        db: Session,
        user: User,
        action: str,
        entity_type: str,
        entity_id: int,
        entity_name: Optional[str] = None,
        field_name: Optional[str] = None,
        old_value: Any = None,
        new_value: Any = None,
        change_summary: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        additional_context: Optional[Dict] = None
    ) -> AuditLog:
        """Create an audit log entry"""
        # Serialize complex values to JSON
        old_val = AuditService._serialize_value(old_value)
        new_val = AuditService._serialize_value(new_value)
        context = json.dumps(additional_context) if additional_context else None
        
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user.id,
            user_email=user.email,
            user_full_name=user.full_name or None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            field_name=field_name,
            old_value=old_val,
            new_value=new_val,
            change_summary=change_summary,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            additional_context=context
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log
    
    @staticmethod
    def log_create(
        db: Session,
        user: User,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        entity_data: Dict,
        **kwargs
    ) -> AuditLog:
        """Log a CREATE action"""
        return AuditService.log_action(
            db=db,
            user=user,
            action='CREATE',
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            new_value=entity_data,
            change_summary=f"Created {entity_type}: {entity_name}",
            **kwargs
        )
    
    @staticmethod
    def log_update(
        db: Session,
        user: User,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        changes: Dict[str, tuple],
        **kwargs
    ) -> list[AuditLog]:
        """Log an UPDATE action with field-level changes"""
        audit_logs = []
        for field_name, (old_val, new_val) in changes.items():
            log = AuditService.log_action(
                db=db,
                user=user,
                action='UPDATE',
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name,
                field_name=field_name,
                old_value=old_val,
                new_value=new_val,
                change_summary=f"Updated {entity_type} {entity_name}: {field_name}",
                **kwargs
            )
            audit_logs.append(log)
        return audit_logs
    
    @staticmethod
    def log_delete(
        db: Session,
        user: User,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        entity_data: Dict,
        **kwargs
    ) -> AuditLog:
        """Log a DELETE action"""
        return AuditService.log_action(
            db=db,
            user=user,
            action='DELETE',
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            old_value=entity_data,
            change_summary=f"Deleted {entity_type}: {entity_name}",
            **kwargs
        )
    
    @staticmethod
    def log_view(
        db: Session,
        user: User,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        **kwargs
    ) -> AuditLog:
        """Log a VIEW action (for sensitive data)"""
        return AuditService.log_action(
            db=db,
            user=user,
            action='VIEW',
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            change_summary=f"Viewed {entity_type}: {entity_name}",
            **kwargs
        )
    
    @staticmethod
    def log_export(
        db: Session,
        user: User,
        export_type: str,
        filters: Dict,
        record_count: int,
        **kwargs
    ) -> AuditLog:
        """Log a data export"""
        return AuditService.log_action(
            db=db,
            user=user,
            action='EXPORT',
            entity_type=export_type,
            entity_id=0,
            entity_name=f"{export_type} export",
            additional_context={
                'filters': filters,
                'record_count': record_count,
                'format': kwargs.get('format', 'unknown')
            },
            change_summary=f"Exported {record_count} {export_type} records",
            **kwargs
        )
    
    @staticmethod
    def log_login(
        db: Session,
        user: User,
        **kwargs
    ) -> AuditLog:
        """Log a LOGIN action"""
        return AuditService.log_action(
            db=db,
            user=user,
            action='LOGIN',
            entity_type='user',
            entity_id=user.id,
            entity_name=user.email,
            change_summary=f"User logged in: {user.email}",
            **kwargs
        )
    
    @staticmethod
    def log_logout(
        db: Session,
        user: User,
        **kwargs
    ) -> AuditLog:
        """Log a LOGOUT action"""
        return AuditService.log_action(
            db=db,
            user=user,
            action='LOGOUT',
            entity_type='user',
            entity_id=user.id,
            entity_name=user.email,
            change_summary=f"User logged out: {user.email}",
            **kwargs
        )





