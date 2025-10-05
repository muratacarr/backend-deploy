from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from fastapi_pagination import add_pagination

from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import (
    global_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler
)
from app.middleware.logging import LoggingMiddleware
from app.api.v1.router import api_router
from app.db.base import Base, engine

# Create database tables (only if database is configured)
def initialize_database():
    """Initialize database tables and default data"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize default roles and permissions
        from app.db.base import SessionLocal
        from app.services.role_service import RoleService
        from app.services.permission_service import PermissionService
        db = SessionLocal()
        try:
            RoleService.initialize_default_roles(db)
            PermissionService.initialize_default_permissions(db)
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Could not create database tables: {e}")
        logger.warning("Please configure DATABASE_URL in .env file with your Neon connection string")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI Authentication System with JWT, OTP, and Role-Based Access Control",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware
app.add_middleware(LoggingMiddleware)

# Add exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

# Include API routers
app.include_router(api_router, prefix="/api/v1")

# Add pagination
add_pagination(app)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    # Initialize database on startup
    initialize_database()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI Authentication System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
