from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.content import Content
from app.models.user import User
from app.schemas.content import ContentCreate, ContentUpdate
from app.core.logger import logger


class ContentService:
    """Service for managing content operations"""
    
    @staticmethod
    def create_content(db: Session, content_data: ContentCreate, author_id: int) -> Content:
        """Create new content"""
        content = Content(
            title=content_data.title,
            content=content_data.content,
            is_public=content_data.is_public,
            author_id=author_id
        )
        
        db.add(content)
        db.commit()
        db.refresh(content)
        
        logger.info(f"Content created: {content.title} by user {author_id}")
        return content
    
    @staticmethod
    def get_content_by_id(db: Session, content_id: int, include_deleted: bool = False) -> Optional[Content]:
        """Get content by ID"""
        query = db.query(Content).filter(Content.id == content_id)
        
        if not include_deleted:
            query = query.filter(Content.is_deleted.is_(False))
        
        return query.first()
    
    @staticmethod
    def get_contents(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        include_deleted: bool = False,
        author_id: Optional[int] = None,
        is_public: Optional[bool] = None
    ) -> List[Content]:
        """Get contents with filters"""
        query = db.query(Content)
        
        if not include_deleted:
            query = query.filter(Content.is_deleted.is_(False))
        
        if author_id:
            query = query.filter(Content.author_id == author_id)
        
        if is_public is not None:
            query = query.filter(Content.is_public == is_public)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_content(db: Session, content_id: int, content_data: ContentUpdate, user_id: int) -> Content:
        """Update content (only by author or admin)"""
        content = ContentService.get_content_by_id(db, content_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check if user is author or admin
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only author or admin can update
        if content.author_id != user_id and user.role.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this content"
            )
        
        # Update fields
        update_data = content_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(content, field, value)
        
        db.commit()
        db.refresh(content)
        
        logger.info(f"Content updated: {content.title} by user {user_id}")
        return content
    
    @staticmethod
    def delete_content(db: Session, content_id: int, user_id: int) -> Content:
        """Soft delete content (only by author or admin)"""
        content = ContentService.get_content_by_id(db, content_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check if user is author or admin
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only author or admin can delete
        if content.author_id != user_id and user.role.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this content"
            )
        
        # Soft delete
        content.soft_delete()
        db.commit()
        
        logger.info(f"Content deleted: {content.title} by user {user_id}")
        return content
    
    @staticmethod
    def moderate_content(db: Session, content_id: int, moderation_data, moderator_id: int) -> Content:
        """Moderate content (moderator/admin only)"""
        content = ContentService.get_content_by_id(db, content_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Moderate content
        content.moderate(moderation_data.status)
        db.commit()
        db.refresh(content)
        
        logger.info(f"Content moderated: {content.title} by user {moderator_id} - Status: {moderation_data.status}")
        return content
