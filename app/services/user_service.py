from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List

from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserUpdateRole
from app.core.security import get_password_hash
from app.core.logger import logger


class UserService:
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int, include_deleted: bool = False) -> Optional[User]:
        """Get user by ID"""
        query = db.query(User).filter(User.id == user_id)
        if not include_deleted:
            query = query.filter(User.is_deleted == False)
        return query.first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str, include_deleted: bool = False) -> Optional[User]:
        """Get user by email"""
        query = db.query(User).filter(User.email == email)
        if not include_deleted:
            query = query.filter(User.is_deleted == False)
        return query.first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str, include_deleted: bool = False) -> Optional[User]:
        """Get user by username"""
        query = db.query(User).filter(User.username == username)
        if not include_deleted:
            query = query.filter(User.is_deleted == False)
        return query.first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> List[User]:
        """Get all users"""
        query = db.query(User)
        if not include_deleted:
            query = query.filter(User.is_deleted == False)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate, role_id: Optional[int] = None) -> User:
        """Create a new user"""
        # Check if user already exists
        if UserService.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if UserService.get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Get role_id (from parameter, user_data, or default to 'user' role)
        if role_id is None:
            role_id = user_data.role_id
        
        if role_id is None:
            # Get default 'user' role
            default_role = db.query(Role).filter(Role.name == "user").first()
            if not default_role:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Default user role not found. Please initialize roles."
                )
            role_id = default_role.id
        
        # Verify role exists
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )
        
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role_id=role_id
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User created: {new_user.email} with role: {role.name}")
        return new_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """Update user information"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check email uniqueness if being updated
        if user_data.email and user_data.email != user.email:
            if UserService.get_user_by_email(db, user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = user_data.email
        
        # Check username uniqueness if being updated
        if user_data.username and user_data.username != user.username:
            if UserService.get_user_by_username(db, user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = user_data.username
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.password:
            user.hashed_password = get_password_hash(user_data.password)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated: {user.email}")
        return user
    
    @staticmethod
    def update_user_role(db: Session, user_id: int, role_data: UserUpdateRole) -> User:
        """Update user role (admin only)"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify role exists
        role = db.query(Role).filter(Role.id == role_data.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )
        
        user.role_id = role_data.role_id
        db.commit()
        db.refresh(user)
        
        logger.info(f"User role updated: {user.email} -> {role.name}")
        return user
    
    @staticmethod
    def soft_delete_user(db: Session, user_id: int) -> User:
        """Soft delete a user"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.soft_delete()
        db.commit()
        db.refresh(user)
        
        logger.info(f"User soft deleted: {user.email}")
        return user
    
    @staticmethod
    def activate_user(db: Session, user_id: int) -> User:
        """Activate a user account"""
        user = UserService.get_user_by_id(db, user_id, include_deleted=True)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        db.commit()
        db.refresh(user)
        
        logger.info(f"User activated: {user.email}")
        return user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> User:
        """Deactivate a user account"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        db.commit()
        db.refresh(user)
        
        logger.info(f"User deactivated: {user.email}")
        return user
