from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import asyncio

from app.models.otp import OTP
from app.core.security import generate_otp
from app.core.logger import logger


class OTPService:
    
    @staticmethod
    async def create_otp(db: Session, email: str, purpose: str = "registration") -> OTP:
        """Create a new OTP for the given email"""
        # Invalidate any existing unused OTPs for this email and purpose
        existing_otps = db.query(OTP).filter(
            OTP.email == email,
            OTP.purpose == purpose,
            OTP.is_used == False
        ).all()
        
        for otp in existing_otps:
            otp.mark_as_used()
        
        # Generate new OTP
        code = generate_otp()
        new_otp = OTP(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=OTP.calculate_expiry()
        )
        
        db.add(new_otp)
        db.commit()
        db.refresh(new_otp)
        
        logger.info(f"OTP created for {email} with purpose {purpose}")
        
        # Send OTP via email
        try:
            from app.services.email_service import EmailService
            email_sent = await EmailService.send_otp_email(email, code, purpose)
            if email_sent:
                logger.info(f"OTP email sent successfully to {email}")
            else:
                logger.warning(f"Failed to send OTP email to {email}")
        except Exception as e:
            logger.error(f"Error sending OTP email: {str(e)}")
        
        # Also log for development (REMOVE IN PRODUCTION!)
        logger.debug(f"OTP Code for {email}: {code}")
        
        return new_otp
    
    @staticmethod
    def verify_otp(db: Session, email: str, code: str, purpose: str = "registration") -> bool:
        """Verify an OTP code"""
        otp = db.query(OTP).filter(
            OTP.email == email,
            OTP.code == code,
            OTP.purpose == purpose,
            OTP.is_used == False
        ).order_by(OTP.created_at.desc()).first()
        
        if not otp:
            logger.warning(f"Invalid OTP attempt for {email}")
            return False
        
        if not otp.is_valid():
            logger.warning(f"Expired OTP attempt for {email}")
            return False
        
        return True
    
    @staticmethod
    async def verify_otp(db: Session, email: str, code: str, purpose: str = "registration"):
        """Verify an OTP code and return user"""
        from app.models.user import User
        
        otp = db.query(OTP).filter(
            OTP.email == email,
            OTP.code == code,
            OTP.purpose == purpose,
            OTP.is_used == False
        ).order_by(OTP.created_at.desc()).first()
        
        if not otp:
            logger.warning(f"Invalid OTP attempt for {email}")
            return None
        
        if not otp.is_valid():
            logger.warning(f"Expired OTP attempt for {email}")
            return None
        
        # Mark OTP as used
        otp.mark_as_used()
        db.commit()
        
        # Get user
        user = db.query(User).filter(User.email == email).first()
        return user
    
    @staticmethod
    def mark_otp_used(db: Session, email: str, code: str, purpose: str = "registration"):
        """Mark an OTP as used"""
        otp = db.query(OTP).filter(
            OTP.email == email,
            OTP.code == code,
            OTP.purpose == purpose,
            OTP.is_used == False
        ).first()
        
        if otp:
            otp.mark_as_used()
            db.commit()
            logger.info(f"OTP marked as used for {email}")
