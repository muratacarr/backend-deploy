from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Optional
import jwt
from fastapi import HTTPException, status

from app.models.blacklisted_token import BlacklistedToken
from app.core.config import settings
from app.core.logger import logger


class TokenBlacklistService:
    """Service for managing blacklisted tokens"""
    
    @staticmethod
    def add_token_to_blacklist(db: Session, token: str, user_id: Optional[int] = None, token_type: str = "access") -> BlacklistedToken:
        """Add token to blacklist"""
        try:
            # Decode token to get JTI, expiration, and user_id
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            jti = payload.get("jti")
            exp = payload.get("exp")
            token_user_id = payload.get("sub")
            
            if not jti or not exp:
                raise ValueError("Invalid token structure")
            
            # Use provided user_id or extract from token
            final_user_id = user_id if user_id is not None else int(token_user_id)
            
            # Convert exp timestamp to datetime
            expires_at = datetime.fromtimestamp(exp)
            
            # Check if token is already blacklisted
            existing = db.query(BlacklistedToken).filter(
                and_(
                    BlacklistedToken.token_jti == jti,
                    BlacklistedToken.user_id == final_user_id
                )
            ).first()
            
            if existing:
                existing.is_revoked = True
                db.commit()
                return existing
            
            # Create new blacklist entry
            blacklisted_token = BlacklistedToken(
                token_jti=jti,
                user_id=final_user_id,
                token_type=token_type,
                expires_at=expires_at,
                is_revoked=True
            )
            
            db.add(blacklisted_token)
            db.commit()
            db.refresh(blacklisted_token)
            
            logger.info(f"Token blacklisted for user {final_user_id}, JTI: {jti}")
            return blacklisted_token
            
        except jwt.ExpiredSignatureError:
            # Token is already expired, no need to blacklist
            logger.info(f"Token already expired for user {final_user_id if 'final_user_id' in locals() else 'unknown'}")
            return None
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to blacklist token"
            )
    
    @staticmethod
    def is_token_blacklisted(db: Session, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            # Decode token to get JTI
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            jti = payload.get("jti")
            
            if not jti:
                return False
            
            # Check if token is blacklisted
            blacklisted = db.query(BlacklistedToken).filter(
                and_(
                    BlacklistedToken.token_jti == jti,
                    BlacklistedToken.is_revoked == True
                )
            ).first()
            
            return blacklisted is not None
            
        except jwt.ExpiredSignatureError:
            # Token is expired, consider it invalid
            return True
        except Exception as e:
            logger.error(f"Error checking token blacklist: {str(e)}")
            return False
    
    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int) -> int:
        """Revoke all tokens for a user"""
        try:
            # Mark all user tokens as revoked
            updated = db.query(BlacklistedToken).filter(
                and_(
                    BlacklistedToken.user_id == user_id,
                    BlacklistedToken.is_revoked is False
                )
            ).update({"is_revoked": True})
            
            db.commit()
            
            logger.info(f"Revoked {updated} tokens for user {user_id}")
            return updated
            
        except Exception as e:
            logger.error(f"Error revoking user tokens: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke user tokens"
            )
    
    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Clean up expired tokens from blacklist"""
        try:
            # Delete expired tokens
            deleted = db.query(BlacklistedToken).filter(
                BlacklistedToken.expires_at < datetime.utcnow()
            ).delete()
            
            db.commit()
            
            logger.info(f"Cleaned up {deleted} expired tokens")
            return deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {str(e)}")
            return 0
