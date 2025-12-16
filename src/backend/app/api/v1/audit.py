from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLog as AuditLogSchema
from app.schemas.common import PaginatedResponse
from app.api.dependencies import get_current_admin_user

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AuditLogSchema])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Get audit logs with filtering (admin only)"""
    query = db.query(AuditLog)
    
    # Apply filters
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if search:
        search_filter = or_(
            AuditLog.entity_name.ilike(f"%{search}%"),
            AuditLog.user_email.ilike(f"%{search}%"),
            AuditLog.user_full_name.ilike(f"%{search}%"),
            AuditLog.change_summary.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count
    total = query.count()
    
    # Apply ordering and pagination
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "items": logs,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLogSchema])
def get_entity_audit_trail(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get complete audit trail for a specific entity (admin only)"""
    logs = db.query(AuditLog).filter(
        and_(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        )
    ).order_by(AuditLog.timestamp.asc()).all()
    
    return logs


@router.get("/export")
def export_audit_logs(
    format: str = Query("csv", regex="^(csv|json)$"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Export audit logs (admin only)"""
    # Build query with same filters as get_audit_logs
    query = db.query(AuditLog)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(AuditLog.timestamp.desc()).all()
    
    if format == "csv":
        import csv
        from io import StringIO
        from fastapi.responses import Response
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Timestamp", "User ID", "User Email", "User Full Name",
            "Action", "Entity Type", "Entity ID", "Entity Name", "Field Name",
            "Old Value", "New Value", "Change Summary", "IP Address", "User Agent"
        ])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.id, log.timestamp.isoformat(), log.user_id, log.user_email,
                log.user_full_name or "", log.action, log.entity_type, log.entity_id,
                log.entity_name or "", log.field_name or "", log.old_value or "",
                log.new_value or "", log.change_summary or "", log.ip_address or "",
                log.user_agent or ""
            ])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
        )
    else:  # JSON
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=[{
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "user_id": log.user_id,
                "user_email": log.user_email,
                "user_full_name": log.user_full_name,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "entity_name": log.entity_name,
                "field_name": log.field_name,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "change_summary": log.change_summary,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "session_id": log.session_id,
                "additional_context": log.additional_context
            } for log in logs]
        )





