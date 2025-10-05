from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.audit_log import AuditLog
from app.core.logger import logger


class AuditService:
    
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success"
    ) -> AuditLog:
        """Log an action to the audit log"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        logger.info(
            f"Audit log created: {action} by user {user_id} on {resource} "
            f"({resource_id}) - Status: {status}"
        )
        
        return audit_log
