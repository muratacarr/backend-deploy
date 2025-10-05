from sqlalchemy.orm import Session
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import role_permissions
from app.core.logger import logger


class PermissionService:
    """Service for managing permissions and role-permission relationships"""
    
    @staticmethod
    def create_permission(db: Session, name: str, description: str = None) -> Permission:
        """Create a new permission"""
        permission = Permission(
            name=name,
            description=description
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        logger.info(f"Permission created: {name}")
        return permission
    
    @staticmethod
    def get_permission_by_name(db: Session, name: str) -> Permission:
        """Get permission by name"""
        return db.query(Permission).filter(Permission.name == name).first()
    
    @staticmethod
    def assign_permission_to_role(db: Session, role_name: str, permission_name: str):
        """Assign a permission to a role"""
        role = db.query(Role).filter(Role.name == role_name).first()
        permission = db.query(Permission).filter(Permission.name == permission_name).first()
        
        if role and permission:
            if permission not in role.permissions:
                role.permissions.append(permission)
                db.commit()
                logger.info(f"Permission '{permission_name}' assigned to role '{role_name}'")
            # Remove the warning log to reduce noise
        else:
            logger.error(f"Role '{role_name}' or permission '{permission_name}' not found")
    
    @staticmethod
    def get_user_permissions(db: Session, user_id: int) -> list:
        """Get all permissions for a user based on their role"""
        from app.models.user import User
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.role:
            return []
        
        return [perm.name for perm in user.role.permissions]
    
    @staticmethod
    def initialize_default_permissions(db: Session):
        """Initialize default permissions for the system"""
        permissions = [
            # User permissions
            ("user_read", "Read user information"),
            ("user_update_own", "Update own profile"),
            
            # Content permissions
            ("content_read", "Read content"),
            ("content_create", "Create content"),
            ("content_update_own", "Update own content"),
            ("content_delete_own", "Delete own content"),
            
            # Moderation permissions
            ("content_moderate", "Moderate content"),
            ("user_moderate", "Moderate users"),
            ("report_manage", "Manage reports"),
            
            # Admin permissions
            ("user_manage", "Manage all users"),
            ("role_manage", "Manage roles and permissions"),
            ("system_manage", "Manage system settings"),
            ("audit_view", "View audit logs"),
        ]
        
        # Create permissions if they don't exist
        for perm_name, perm_desc in permissions:
            existing = db.query(Permission).filter(Permission.name == perm_name).first()
            if not existing:
                PermissionService.create_permission(db, perm_name, perm_desc)
        
        # Check if permissions are already assigned to avoid duplicate assignments
        role_permissions_map = {
            "user": [
                "user_read", "user_update_own",
                "content_read", "content_create", "content_update_own", "content_delete_own"
            ],
            "moderator": [
                "user_read", "user_update_own",
                "content_read", "content_create", "content_update_own", "content_delete_own",
                "content_moderate", "user_moderate", "report_manage"
            ],
            "admin": [
                "user_read", "user_update_own",
                "content_read", "content_create", "content_update_own", "content_delete_own",
                "content_moderate", "user_moderate", "report_manage",
                "user_manage", "role_manage", "system_manage", "audit_view"
            ]
        }
        
        # Check if any role already has permissions assigned
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role and len(admin_role.permissions) > 0:
            logger.info("Permissions already initialized, skipping assignment")
            return
        
        # Assign permissions to roles only if not already assigned
        for role_name, perm_names in role_permissions_map.items():
            for perm_name in perm_names:
                PermissionService.assign_permission_to_role(db, role_name, perm_name)
        
        logger.info("Default permissions initialized and assigned to roles")
