"""
Structured logging for the MentraOS Python SDK

Provides JSON-structured logging similar to Pino.js used in the TypeScript SDK.
All logs are output as JSON objects for machine readability and easy parsing.
"""

import logging
import sys
from typing import Any, Dict, Optional
import structlog
from structlog.stdlib import LoggerFactory


def setup_logging(
    level: str = "INFO",
    logger_name: str = "mentra_sdk",
    service_name: str = "mentra_sdk"
) -> structlog.stdlib.BoundLogger:
    """
    Setup structured JSON logging

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        logger_name: Name for the logger
        service_name: Service name to include in logs

    Returns:
        Configured structlog logger
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )

    # Configure structlog
    structlog.configure(
        processors=[
            # Add service name to all logs
            structlog.processors.add_log_level,
            structlog.processors.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Create and return the logger
    logger = structlog.get_logger(logger_name)
    return logger.bind(service=service_name)


# Create default logger instance
logger = setup_logging()


def get_logger(
    name: str,
    **context: Any
) -> structlog.stdlib.BoundLogger:
    """
    Get a logger with additional context

    Args:
        name: Logger name (typically __name__)
        **context: Additional context to bind to logger

    Returns:
        Logger with bound context
    """
    return structlog.get_logger(name).bind(**context)


def create_session_logger(
    session_id: str,
    user_id: str,
    package_name: str,
    **extra_context: Any
) -> structlog.stdlib.BoundLogger:
    """
    Create a logger with session-specific context

    Args:
        session_id: Session identifier
        user_id: User identifier
        package_name: App package name
        **extra_context: Additional context

    Returns:
        Session-scoped logger
    """
    return get_logger(
        "session",
        session_id=session_id,
        user_id=user_id,
        package_name=package_name,
        **extra_context
    )


def create_app_logger(
    package_name: str,
    **extra_context: Any
) -> structlog.stdlib.BoundLogger:
    """
    Create a logger with app-specific context

    Args:
        package_name: App package name
        **extra_context: Additional context

    Returns:
        App-scoped logger
    """
    return get_logger(
        "app",
        package_name=package_name,
        **extra_context
    )