from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.auth import (
    Token,
    LoginRequest,
    RefreshTokenRequest,
    OTPRequest,
    RegisterRequest,
    RegisterResponse,
    VerifyAccountRequest
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService
from app.services.audit_service import AuditService
from app.services.token_blacklist_service import TokenBlacklistService
from app.api.deps import get_current_user, get_client_ip, get_user_agent
from app.models.user import User
from app.core.logger import logger

# OAuth2 scheme for token extraction
oauth2_scheme = HTTPBearer()

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user (Step 1: Create account)"""
    try:
        # Create user
        user = AuthService.register_user(db, user_data)
        
        # Send OTP
        await OTPService.create_otp(db, user.email, purpose="registration")
        
        # Log audit
        AuditService.log_action(
            db=db,
            action="user_registration_initiated",
            user_id=user.id,
            resource="user",
            resource_id=str(user.id),
            details={"email": user.email, "username": user.username},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        return RegisterResponse(
            message="Registration successful. Please check your email for OTP code.",
            email=user.email,
            user_id=user.id,
            requires_verification=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/verify-account", response_model=UserResponse, status_code=status.HTTP_200_OK)
def verify_account(
    verify_data: VerifyAccountRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify user account with OTP (Step 2: Verify account)"""
    try:
        user = AuthService.verify_user_account(db, verify_data)
        
        # Log audit
        AuditService.log_action(
            db=db,
            action="user_account_verified",
            user_id=user.id,
            resource="user",
            resource_id=str(user.id),
            details={"email": user.email},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during account verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account verification failed"
        )


@router.post("/resend-otp", status_code=status.HTTP_200_OK)
async def resend_otp(
    otp_request: OTPRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Resend OTP code to user"""
    try:
        # Check if user exists
        user = db.query(User).filter(
            User.email == otp_request.email,
            User.is_deleted is False
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified is True:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account already verified"
            )
        
        # Create new OTP
        await OTPService.create_otp(db, otp_request.email, purpose="registration")
        
        # Log audit
        AuditService.log_action(
            db=db,
            action="otp_resend",
            user_id=user.id,
            resource="otp",
            details={"email": otp_request.email},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        return {
            "message": "OTP sent successfully",
            "email": otp_request.email,
            "expires_in_minutes": 5
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend OTP"
        )


@router.post("/login")
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login user - Step 1: Verify credentials and send OTP"""
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        # Log failed attempt
        AuditService.log_action(
            db=db,
            action="login_failed",
            resource="auth",
            details={"email": login_data.email},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="failed"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user account is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not verified. Please verify your account first."
        )
    
    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive. Please contact administrator."
        )
    
    # Send OTP for login verification
    await OTPService.create_otp(db, user.email, purpose="login")
    
    # Log OTP sent
    AuditService.log_action(
        db=db,
        action="login_otp_sent",
        user_id=user.id,
        resource="auth",
        details={"email": user.email},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status="success"
    )
    
    return {
        "message": "OTP sent to your email. Please verify to complete login.",
        "email": user.email,
        "requires_otp_verification": True,
        "expires_in_minutes": 5
    }


@router.post("/verify-login", response_model=Token)
async def verify_login(
    verify_data: VerifyAccountRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login user - Step 2: Verify OTP and return JWT tokens"""
    try:
        # Verify OTP
        user = await OTPService.verify_otp(db, verify_data.email, verify_data.otp_code, purpose="login")
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code"
            )
        
        # Create tokens
        tokens = AuthService.create_tokens(user.id, db)
        
        # Log successful login
        AuditService.log_action(
            db=db,
            action="login_success",
            user_id=user.id,
            resource="auth",
            details={"email": user.email},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login verification failed"
        )


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    try:
        # First blacklist the old refresh token
        TokenBlacklistService.add_token_to_blacklist(
            db=db,
            token=refresh_data.refresh_token,
            user_id=None,  # Will be extracted from token
            token_type="refresh"
        )
        
        # Create new tokens
        tokens = AuthService.refresh_access_token(db, refresh_data.refresh_token)
        
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    """Logout user and blacklist token"""
    try:
        # Add current token to blacklist
        TokenBlacklistService.add_token_to_blacklist(
            db=db,
            token=credentials.credentials,
            user_id=current_user.id,
            token_type="access"
        )
        
        # Log logout
        AuditService.log_action(
            db=db,
            action="logout",
            user_id=current_user.id,
            resource="auth",
            details={"email": current_user.email},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        # Still log the logout attempt even if blacklisting fails
        AuditService.log_action(
            db=db,
            action="logout",
            user_id=current_user.id,
            resource="auth",
            details={"email": current_user.email, "error": str(e)},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="partial_success"
        )
        
        return {"message": "Logged out (token blacklisting may have failed)"}




@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user
