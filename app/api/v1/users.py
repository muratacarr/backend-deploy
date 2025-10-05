from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi_pagination import Page, paginate

from app.db.base import get_db
from app.schemas.user import UserResponse, UserUpdate, UserUpdateRole
from app.services.user_service import UserService
from app.services.audit_service import AuditService
from app.api.deps import (
    get_current_user,
    require_permission,
    get_client_ip,
    get_user_agent
)
from app.services.permission_service import PermissionService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=Page[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user_manage"))
):
    """List all users (Admin/Moderator only)"""
    users = UserService.get_users(db, skip=0, limit=1000)
    return paginate(users)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    # Users can only view their own profile unless they have user_manage permission
    if current_user.id != user_id and "user_manage" not in PermissionService.get_user_permissions(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user information"""
    # Users can only update their own profile unless they are admin
    if current_user.id != user_id and current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    user = UserService.update_user(db, user_id, user_data)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="user_update",
        user_id=current_user.id,
        resource="user",
        resource_id=str(user_id),
        details={"updated_by": current_user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return user


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: UserUpdateRole,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user_manage"))
):
    """Update user role (admin only)"""
    user = UserService.update_user_role(db, user_id, role_data)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="user_role_update",
        user_id=current_user.id,
        resource="user",
        resource_id=str(user_id),
        details={
            "updated_by": current_user.email,
            "new_role_id": role_data.role_id
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return user


@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user_manage"))
):
    """Soft delete user (admin only)"""
    user = UserService.soft_delete_user(db, user_id)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="user_delete",
        user_id=current_user.id,
        resource="user",
        resource_id=str(user_id),
        details={"deleted_by": current_user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return user


@router.post("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user_manage"))
):
    """Activate user account (admin only)"""
    user = UserService.activate_user(db, user_id)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="user_activate",
        user_id=current_user.id,
        resource="user",
        resource_id=str(user_id),
        details={"activated_by": current_user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return user


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user_manage"))
):
    """Deactivate user account (admin only)"""
    user = UserService.deactivate_user(db, user_id)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="user_deactivate",
        user_id=current_user.id,
        resource="user",
        resource_id=str(user_id),
        details={"deactivated_by": current_user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return user
