from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi_pagination import Page, paginate

from app.db.base import get_db
from app.models.user import User
from app.api.deps import require_permission, get_client_ip, get_user_agent
from app.services.audit_service import AuditService
from app.services.content_service import ContentService
from app.schemas.content import ContentCreate, ContentUpdate, ContentResponse, ContentModeration

router = APIRouter()


@router.post("/", response_model=ContentResponse)
def create_content(
    content_data: ContentCreate,
    request: Request,
    current_user: User = Depends(require_permission("content_create")),
    db: Session = Depends(get_db)
):
    """Create new content (All authenticated users) - Content creation"""
    try:
        content = ContentService.create_content(db, content_data, current_user.id)
        
        # Log audit
        AuditService.log_action(
            db=db,
            action="content_created",
            user_id=current_user.id,
            resource="content",
            resource_id=str(content.id),
            details={"title": content.title, "is_public": content.is_public},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        return content
        
    except Exception as e:
        # Log failed attempt
        AuditService.log_action(
            db=db,
            action="content_creation_failed",
            user_id=current_user.id,
            resource="content",
            details={"title": content_data.title, "error": str(e)},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="failed"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content"
        )


@router.get("/", response_model=Page[ContentResponse])
def get_content(
    skip: int = 0,
    limit: int = 100,
    is_public: Optional[bool] = None,
    current_user: User = Depends(require_permission("content_read")),
    db: Session = Depends(get_db)
):
    """Get content (All authenticated users) - Content viewing"""
    try:
        # Get contents with filters
        contents = ContentService.get_contents(
            db=db,
            skip=skip,
            limit=limit,
            is_public=is_public
        )
        
        return paginate(contents)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content"
        )


@router.get("/{content_id}", response_model=ContentResponse)
def get_content_by_id(
    content_id: int,
    current_user: User = Depends(require_permission("content_read")),
    db: Session = Depends(get_db)
):
    """Get specific content by ID"""
    content = ContentService.get_content_by_id(db, content_id)
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if user can view this content
    if not content.is_public and content.author_id != current_user.id and current_user.role.name not in ["admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this content"
        )
    
    return content


@router.put("/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: int,
    content_data: ContentUpdate,
    request: Request,
    current_user: User = Depends(require_permission("content_update_own")),
    db: Session = Depends(get_db)
):
    """Update own content (All authenticated users) - Own content modification"""
    try:
        content = ContentService.update_content(db, content_id, content_data, current_user.id)
        
        # Log audit
        AuditService.log_action(
            db=db,
            action="content_updated",
            user_id=current_user.id,
            resource="content",
            resource_id=str(content_id),
            details={"title": content.title, "updated_fields": list(content_data.dict(exclude_unset=True).keys())},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        # Log failed attempt
        AuditService.log_action(
            db=db,
            action="content_update_failed",
            user_id=current_user.id,
            resource="content",
            resource_id=str(content_id),
            details={"error": str(e)},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="failed"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update content"
        )


@router.delete("/{content_id}")
def delete_content(
    content_id: int,
    request: Request,
    current_user: User = Depends(require_permission("content_delete_own")),
    db: Session = Depends(get_db)
):
    """Delete own content (All authenticated users) - Own content deletion"""
    try:
        content = ContentService.delete_content(db, content_id, current_user.id)
        
        # Log audit
        AuditService.log_action(
            db=db,
            action="content_deleted",
            user_id=current_user.id,
            resource="content",
            resource_id=str(content_id),
            details={"title": content.title},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        return {"message": f"Content '{content.title}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        # Log failed attempt
        AuditService.log_action(
            db=db,
            action="content_deletion_failed",
            user_id=current_user.id,
            resource="content",
            resource_id=str(content_id),
            details={"error": str(e)},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="failed"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete content"
        )


@router.put("/{content_id}/moderate")
def moderate_content(
    content_id: int,
    moderation_data: ContentModeration,
    request: Request,
    current_user: User = Depends(require_permission("content_moderate")),
    db: Session = Depends(get_db)
):
    """Moderate content (Moderator/Admin only) - Content moderation"""
    try:
        content = ContentService.moderate_content(db, content_id, moderation_data, current_user.id)
        
        # Log audit
        AuditService.log_action(
            db=db,
            action="content_moderated",
            user_id=current_user.id,
            resource="content",
            resource_id=str(content_id),
            details={
                "title": content.title,
                "moderation_status": moderation_data.status,
                "reason": moderation_data.reason
            },
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        return {
            "message": f"Content '{content.title}' moderated successfully",
            "status": moderation_data.status,
            "content": content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log failed attempt
        AuditService.log_action(
            db=db,
            action="content_moderation_failed",
            user_id=current_user.id,
            resource="content",
            resource_id=str(content_id),
            details={"error": str(e)},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="failed"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to moderate content"
        )
