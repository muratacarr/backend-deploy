from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from app.core.logger import logger


class RoleService:
    
    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        """Get role by name"""
        return db.query(Role).filter(Role.name == name).first()
    
    @staticmethod
    def get_roles(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Role]:
        """Get all roles"""
        query = db.query(Role)
        if active_only:
            query = query.filter(Role.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role:
        """Create a new role"""
        # Check if role already exists
        existing_role = RoleService.get_role_by_name(db, role_data.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists"
            )
        
        new_role = Role(
            name=role_data.name,
            description=role_data.description
        )
        
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        
        logger.info(f"Role created: {new_role.name}")
        return new_role
    
    @staticmethod
    def update_role(db: Session, role_id: int, role_data: RoleUpdate) -> Role:
        """Update role information"""
        role = RoleService.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Check name uniqueness if being updated
        if role_data.name and role_data.name != role.name:
            existing_role = RoleService.get_role_by_name(db, role_data.name)
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role name already in use"
                )
            role.name = role_data.name
        
        if role_data.description is not None:
            role.description = role_data.description
        
        if role_data.is_active is not None:
            role.is_active = role_data.is_active
        
        db.commit()
        db.refresh(role)
        
        logger.info(f"Role updated: {role.name}")
        return role
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> Role:
        """Delete a role (soft delete by deactivating)"""
        role = RoleService.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Check if role is in use
        from app.models.user import User
        users_with_role = db.query(User).filter(User.role_id == role_id).count()
        if users_with_role > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role. {users_with_role} users are using this role."
            )
        
        role.is_active = False
        db.commit()
        db.refresh(role)
        
        logger.info(f"Role deactivated: {role.name}")
        return role
    
    @staticmethod
    def initialize_default_roles(db: Session):
        """Initialize default roles if they don't exist"""
        default_roles = [
            {"name": "admin", "description": "Administrator with full access"},
            {"name": "moderator", "description": "Moderator with limited admin access"},
            {"name": "user", "description": "Regular user with basic access"}
        ]
        
        for role_data in default_roles:
            existing_role = RoleService.get_role_by_name(db, role_data["name"])
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
                logger.info(f"Created default role: {role_data['name']}")
        
        db.commit()
        logger.info("Default roles initialized")
