"""Logging configuration and utilities."""

import logging
import sys
from typing import Optional
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    structured: bool = False,
    log_file: Optional[str] = None
) -> None:
    """Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARN, ERROR)
        structured: Use structured JSON logging
        log_file: Optional log file path
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


class AuditLogger:
    """Audit logger for security-relevant events."""
    
    def __init__(self):
        self.logger = logging.getLogger("evomind.audit")
    
    def log_tool_creation(
        self,
        tool_id: str,
        user: str,
        success: bool,
        metadata: dict
    ) -> None:
        """Log tool creation event."""
        self.logger.info(
            "Tool creation",
            extra={
                "event": "tool_creation",
                "tool_id": tool_id,
                "user": user,
                "success": success,
                "metadata": metadata
            }
        )
    
    def log_execution(
        self,
        tool_id: str,
        user: str,
        success: bool,
        duration_ms: float
    ) -> None:
        """Log tool execution."""
        self.logger.info(
            "Tool execution",
            extra={
                "event": "tool_execution",
                "tool_id": tool_id,
                "user": user,
                "success": success,
                "duration_ms": duration_ms
            }
        )
    
    def log_policy_violation(
        self,
        violation_type: str,
        tool_id: str,
        details: dict
    ) -> None:
        """Log policy violation."""
        self.logger.warning(
            "Policy violation",
            extra={
                "event": "policy_violation",
                "violation_type": violation_type,
                "tool_id": tool_id,
                "details": details
            }
        )
