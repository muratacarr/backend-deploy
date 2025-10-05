from fastapi import APIRouter
from app.api.v1 import auth, users, roles, audit_logs, admin, moderator, content

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(moderator.router, prefix="/moderator", tags=["Moderator"])
api_router.include_router(content.router, prefix="/content", tags=["Content"])
