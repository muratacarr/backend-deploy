from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime, timedelta

from app.models.user import User
from app.models.role import Role
from app.models.otp import OTP
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp
)
from app.schemas.auth import RegisterRequest, VerifyAccountRequest
from app.core.logger import logger


class AuthService:
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
    
    @staticmethod
    def create_tokens(user_id: int, db: Session) -> dict:
        """Create access and refresh tokens with extended payload"""
        # Get user details
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user role and permissions
        user_role = db.query(Role).filter(Role.id == user.role_id).first()
        permissions = []
        if user_role:
            permissions = [perm.name for perm in user_role.permissions] if hasattr(user_role, 'permissions') else []
        
        # Create tokens with extended payload
        token_data = {
            "sub": str(user_id),
            "username": user.username,
            "roles": [user_role.name] if user_role else [],
            "permissions": permissions
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False,
            User.is_active == True
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return AuthService.create_tokens(user_id, db)
    
    @staticmethod
    def register_user(db: Session, user_data: RegisterRequest) -> User:
        """Register a new user (unverified)"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            if existing_user.is_verified:
                # User already exists and verified
                if existing_user.email == user_data.email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
            else:
                # User exists but not verified, update the user
                logger.info(f"Updating unverified user: {existing_user.email}")
                existing_user.username = user_data.username
                existing_user.hashed_password = get_password_hash(user_data.password)
                existing_user.full_name = user_data.full_name
                db.commit()
                db.refresh(existing_user)
                return existing_user
        
        # Get default 'user' role
        default_role = db.query(Role).filter(Role.name == "user").first()
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default user role not found. Please initialize roles."
            )
        
        # Create user (unverified)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role_id=default_role.id,
            is_verified=False,  # Not verified yet
            is_active=False  # Inactive until verified
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered (unverified): {new_user.email}")
        return new_user
    
    @staticmethod
    def verify_user_account(db: Session, verify_data: VerifyAccountRequest) -> User:
        """Verify user account with OTP"""
        # Get user
        user = db.query(User).filter(
            User.email == verify_data.email,
            User.is_deleted == False
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account already verified"
            )
        
        # Verify OTP
        otp = db.query(OTP).filter(
            OTP.email == verify_data.email,
            OTP.code == verify_data.otp_code,
            OTP.purpose == "registration",
            OTP.is_used == False
        ).order_by(OTP.created_at.desc()).first()
        
        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code"
            )
        
        if not otp.is_valid():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP code has expired"
            )
        
        # Mark OTP as used
        otp.mark_as_used()
        
        # Activate and verify user
        user.is_verified = True
        user.is_active = True
        db.commit()
        db.refresh(user)
        
        logger.info(f"User account verified: {user.email}")
        
        # Send welcome email (async, don't wait for it)
        try:
            import asyncio
            from app.services.email_service import EmailService
            asyncio.create_task(EmailService.send_welcome_email(user.email, user.username))
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
        
        return user
