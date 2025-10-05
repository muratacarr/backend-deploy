from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError, jwt
from app.db.base import get_db
from app.models.user import User
from app.core.config import settings
from app.core.logger import logger
from app.services.permission_service import PermissionService
from app.services.token_blacklist_service import TokenBlacklistService

# OAuth2 scheme for token extraction
oauth2_scheme = HTTPBearer()


def get_current_user(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user with blacklist check"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Check if token is blacklisted first
        if TokenBlacklistService.is_token_blacklisted(db, credentials.credentials):
            logger.warning("Attempted to use blacklisted token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is still active
    if not user.is_active or user.is_deleted:
        logger.warning(f"Attempted to use token for inactive/deleted user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        user_permissions = PermissionService.get_user_permissions(db, current_user.id)
        
        if permission not in user_permissions:
            logger.warning(f"User {current_user.id} attempted to access resource requiring permission '{permission}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return current_user
    
    return permission_checker


def require_role(role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        user_role = db.query(User).filter(User.id == current_user.id).first().role
        
        if not user_role or user_role.name != role:
            logger.warning(f"User {current_user.id} attempted to access resource requiring role '{role}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        
        return current_user
    
    return role_checker


def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent from request"""
    return request.headers.get("User-Agent", "unknown")
