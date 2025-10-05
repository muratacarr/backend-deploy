from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User
from app.api.deps import require_permission, get_client_ip, get_user_agent
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(require_permission("user_manage")),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only) - Full user management access"""
    users = db.query(User).filter(User.is_deleted.is_(False)).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(require_permission("user_manage")),
    db: Session = Depends(get_db)
):
    """Get user by ID (Admin only) - Full user details access"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(require_permission("user_manage")),
    db: Session = Depends(get_db)
):
    """Update any user (Admin only) - Full user modification access"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="user_updated_by_admin",
        user_id=current_user.id,
        resource="user",
        resource_id=str(user_id),
        details={"updated_fields": list(user_update.dict(exclude_unset=True).keys())},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_permission("user_manage")),
    db: Session = Depends(get_db)
):
    """Soft delete user (Admin only) - Permanent user removal"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete
    user.is_deleted = True
    user.is_active = False
    db.commit()
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="user_deleted_by_admin",
        user_id=current_user.id,
        resource="user",
        resource_id=str(user_id),
        details={"deleted_user_email": user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return {"message": "User deleted successfully"}


@router.get("/audit-logs")
def get_audit_logs(
    current_user: User = Depends(require_permission("audit_view")),
    db: Session = Depends(get_db)
):
    """Get audit logs (Admin only) - System audit trail access"""
    from app.models.audit_log import AuditLog
    from fastapi_pagination import paginate
    
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
    return paginate(logs)
