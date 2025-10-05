from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.schemas.user import UserResponse
from app.models.user import User
from app.api.deps import require_permission, get_client_ip, get_user_agent
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
def get_users_for_moderation(
    current_user: User = Depends(require_permission("user_moderate")),
    db: Session = Depends(get_db)
):
    """Get users for moderation (Moderator/Admin only) - Limited user access"""
    users = db.query(User).filter(
        User.is_deleted.is_(False),
        User.is_active.is_(True)
    ).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_for_moderation(
    user_id: int,
    current_user: User = Depends(require_permission("user_moderate")),
    db: Session = Depends(get_db)
):
    """Get user for moderation (Moderator/Admin only) - Limited user details"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}/suspend")
def suspend_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_permission("user_moderate")),
    db: Session = Depends(get_db)
):
    """Suspend user (Moderator/Admin only) - Temporary user suspension"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Suspend user
    user.is_active = False
    db.commit()
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="user_suspended_by_moderator",
        user_id=current_user.id,
        resource="user",
        resource_id=str(user_id),
        details={"suspended_user_email": user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return {"message": "User suspended successfully"}


@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_permission("user_moderate")),
    db: Session = Depends(get_db)
):
    """Activate user (Moderator/Admin only) - User reactivation"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Activate user
    user.is_active = True
    db.commit()
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="user_activated_by_moderator",
        user_id=current_user.id,
        resource="user",
        resource_id=str(user_id),
        details={"activated_user_email": user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return {"message": "User activated successfully"}


@router.get("/reports")
def get_reports(
    current_user: User = Depends(require_permission("report_manage")),
    db: Session = Depends(get_db)
):
    """Get reports for moderation (Moderator/Admin only) - Report management"""
    # This would typically query a reports table
    return {"message": "Reports endpoint - to be implemented with reports table"}
