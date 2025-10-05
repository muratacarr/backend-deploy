from sqlalchemy import Column, Integer, ForeignKey, Table
from app.db.base import Base

# Many-to-many association table for roles and permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True)
)
