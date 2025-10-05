from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from fastapi_pagination import Page, paginate
from typing import Optional

from app.db.base import get_db
from app.schemas.audit_log import AuditLogResponse
from app.models.audit_log import AuditLog
from app.api.deps import require_permission
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=Page[AuditLogResponse])
def list_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource: Optional[str] = Query(None, description="Filter by resource"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit_view"))
):
    """List audit logs (moderator/admin only)"""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if resource:
        query = query.filter(AuditLog.resource == resource)
    
    logs = query.order_by(AuditLog.created_at.desc()).all()
    return paginate(logs)


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit_view"))
):
    """Get specific audit log (moderator/admin only)"""
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    return log
