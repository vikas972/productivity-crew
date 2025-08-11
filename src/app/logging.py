"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any, Dict

import structlog


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure structured logging for the application."""
    
    # Set logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(level=numeric_level)
    
    # Configure structlog
    if log_format.lower() == "json":
        # JSON logging for production
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        # Human-readable logging for development
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger instance for this class."""
        return get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs: Any) -> Dict[str, Any]:
    """Create a structured log entry for function calls."""
    return {
        "event": "function_call",
        "function": func_name,
        "parameters": kwargs
    }


def log_agent_execution(agent_name: str, task: str, **kwargs: Any) -> Dict[str, Any]:
    """Create a structured log entry for agent execution."""
    return {
        "event": "agent_execution",
        "agent": agent_name,
        "task": task,
        **kwargs
    }


def log_data_generation(data_type: str, count: int, **kwargs: Any) -> Dict[str, Any]:
    """Create a structured log entry for data generation."""
    return {
        "event": "data_generation",
        "data_type": data_type,
        "count": count,
        **kwargs
    }


def log_validation_result(validation_type: str, passed: bool, errors: list = None, **kwargs: Any) -> Dict[str, Any]:
    """Create a structured log entry for validation results."""
    return {
        "event": "validation_result",
        "validation_type": validation_type,
        "passed": passed,
        "error_count": len(errors) if errors else 0,
        "errors": errors or [],
        **kwargs
    }


def log_export_operation(output_type: str, file_path: str, record_count: int, **kwargs: Any) -> Dict[str, Any]:
    """Create a structured log entry for export operations."""
    return {
        "event": "export_operation",
        "output_type": output_type,
        "file_path": file_path,
        "record_count": record_count,
        **kwargs
    }
