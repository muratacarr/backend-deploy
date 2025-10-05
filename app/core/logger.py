import sys
import os
from loguru import logger
from pathlib import Path

# Check if we're in Vercel (read-only filesystem)
IS_VERCEL = os.environ.get("VERCEL") == "1"

# Remove default handler
logger.remove()

# Add console handler (always works)
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Only add file handlers if not in Vercel
if not IS_VERCEL:
    try:
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Add file handler for all logs
        logger.add(
            "logs/app.log",
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG"
        )
        
        # Add file handler for errors only
        logger.add(
            "logs/error.log",
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR"
        )
    except Exception as e:
        # If file logging fails, just use console logging
        logger.warning(f"File logging not available: {e}")
        logger.warning("Using console logging only")
else:
    # In Vercel, only use console logging
    logger.info("Running in Vercel environment - using console logging only")
