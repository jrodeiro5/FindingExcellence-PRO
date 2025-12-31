"""
Logging setup module using Loguru.

Provides colorful, auto-rotating logs with better context for debugging.
Features:
- Colorful console output with timestamps
- Auto-rotating file logs (10 MB max, 5 backups)
- Structured context (module, function, line number)
- Exception tracebacks with local variables
- Intercepts uvicorn/FastAPI logs
"""

import logging
import sys
from pathlib import Path

from loguru import logger

# Default log file
LOG_FILE = "finding_excellence.log"


class InterceptHandler(logging.Handler):
    """
    Redirect standard library logging to Loguru.

    This allows FastAPI, uvicorn, and other libraries using stdlib logging
    to output through Loguru with consistent formatting.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logged message originated
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(log_file: str = LOG_FILE, level: str = "INFO") -> "logger":
    """
    Set up Loguru logging for the application.

    Features:
    - Colorful console output with timestamps
    - Auto-rotating file logs (10 MB max, 5 days retention)
    - Structured context (module, function, line number)
    - Exception tracebacks with local variables

    Args:
        log_file: Path to the log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured Loguru logger
    """
    # Remove default handler to avoid duplicate output
    logger.remove()

    # Console handler with colors and simplified format
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )

    # File handler with rotation and retention
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {module}:{function}:{line} - {message}",
        level=level,
        rotation="10 MB",      # Rotate when file reaches 10 MB
        retention="5 days",    # Keep logs for 5 days
        compression="zip",     # Compress rotated logs
        backtrace=True,        # Include traceback for exceptions
        diagnose=True,         # Include local variables in exceptions
    )

    # Intercept standard library logging (for FastAPI/uvicorn)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Also intercept uvicorn and fastapi loggers specifically
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    return logger


def get_logger(name: str = None):
    """
    Get a logger instance, optionally with a context name.

    Args:
        name: Optional context name (e.g., module name)

    Returns:
        Loguru logger (optionally with bind context)
    """
    if name:
        return logger.bind(context=name)
    return logger
