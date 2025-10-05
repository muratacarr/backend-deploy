from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String, unique=True, nullable=False, index=True)  # JWT ID
    user_id = Column(Integer, nullable=False, index=True)
    token_type = Column(String, nullable=False)  # access or refresh
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def is_expired(self):
        """Check if token is expired"""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
