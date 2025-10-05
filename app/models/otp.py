from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.db.base import Base
from app.core.config import settings


class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    email = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False)
    purpose = Column(String, nullable=False)  # registration, password_reset, login, etc.
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def is_valid(self) -> bool:
        """Check if OTP is still valid"""
        from datetime import timezone
        return not self.is_used and datetime.now(timezone.utc) < self.expires_at
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
    
    @staticmethod
    def calculate_expiry() -> datetime:
        """Calculate OTP expiry time"""
        from datetime import timezone
        return datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
