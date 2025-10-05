from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base import Base


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Content status
    is_published = Column(Boolean, default=True, nullable=False)
    is_moderated = Column(Boolean, default=False, nullable=False)
    moderation_status = Column(String, default="pending", nullable=False)  # pending, approved, rejected
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="contents")
    
    def soft_delete(self):
        """Soft delete the content"""
        self.is_deleted = True
        self.is_published = False
        self.deleted_at = datetime.utcnow()
    
    def moderate(self, status: str):
        """Moderate the content"""
        self.is_moderated = True
        self.moderation_status = status
        if status == "approved":
            self.is_published = True
        elif status == "rejected":
            self.is_published = False
