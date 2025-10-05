from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi_pagination import Page, paginate

from app.db.base import get_db
from app.schemas.role import RoleResponse, RoleCreate, RoleUpdate
from app.services.role_service import RoleService
from app.services.audit_service import AuditService
from app.api.deps import require_permission, get_client_ip, get_user_agent
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=Page[RoleResponse])
def list_roles(
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("role_manage"))
):
    """List all roles (admin only)"""
    roles = RoleService.get_roles(db, skip=0, limit=1000, active_only=active_only)
    return paginate(roles)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("role_manage"))
):
    """Get role by ID (admin only)"""
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("role_manage"))
):
    """Create a new role (admin only)"""
    role = RoleService.create_role(db, role_data)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="role_create",
        user_id=current_user.id,
        resource="role",
        resource_id=str(role.id),
        details={"name": role.name, "created_by": current_user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return role


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("role_manage"))
):
    """Update role (admin only)"""
    role = RoleService.update_role(db, role_id, role_data)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="role_update",
        user_id=current_user.id,
        resource="role",
        resource_id=str(role_id),
        details={"updated_by": current_user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return role


@router.delete("/{role_id}", response_model=RoleResponse)
def delete_role(
    role_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("role_manage"))
):
    """Delete/deactivate role (admin only)"""
    role = RoleService.delete_role(db, role_id)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="role_delete",
        user_id=current_user.id,
        resource="role",
        resource_id=str(role_id),
        details={"deleted_by": current_user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return role


@router.post("/initialize", status_code=status.HTTP_200_OK)
def initialize_roles(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("role_manage"))
):
    """Initialize default roles (admin only)"""
    RoleService.initialize_default_roles(db)
    
    # Log audit
    AuditService.log_action(
        db=db,
        action="roles_initialize",
        user_id=current_user.id,
        resource="role",
        details={"initialized_by": current_user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return {"message": "Default roles initialized successfully"}
