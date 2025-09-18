"""
Enhanced Logging System for XLR Template Generator - V4

This module provides an improved logging system with:
- Structured logging with context
- Performance tracking
- Error correlation
- Automatic log rotation
- Colored console output
- JSON structured logs for monitoring
"""

import logging
import logging.handlers
import os
import sys
import time
import json
import inspect
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class XLRLogger:
    """
    Enhanced logger for XLR operations with structured logging and context tracking.

    Features:
    - Multiple log levels and handlers
    - Performance timing
    - Error correlation
    - Structured JSON logging
    - Automatic log rotation
    - Context injection
    """

    def __init__(self, release_name: str, log_directory: Optional[str] = None):
        """
        Initialize enhanced XLR logger.

        Args:
            release_name: Name of the release for log organization
            log_directory: Custom log directory (defaults to log/<release_name>)
        """
        self.release_name = release_name
        self.log_dir = Path(log_directory or f"log/{release_name}")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Performance tracking
        self.operation_timers = {}
        self.operation_counters = {
            'api_calls': 0,
            'template_operations': 0,
            'phase_operations': 0,
            'variable_operations': 0,
            'errors': 0
        }

        # Context for structured logging
        self.context = {
            'release_name': release_name,
            'session_id': int(time.time()),
            'version': '4.0-enhanced-logging'
        }

        # Initialize loggers
        self._setup_loggers()

    def _setup_loggers(self):
        """Set up multiple specialized loggers with different handlers."""

        # Main logger for creation report (compatible with existing CR.log format)
        self.logger_cr = self._create_logger(
            'LOG_CR',
            self.log_dir / 'CR.log',
            level=logging.INFO,
            format_type='standard'
        )

        # Detailed logger with JSON structure for monitoring
        self.logger_detail = self._create_logger(
            'LOG_DETAIL',
            self.log_dir / 'detail.jsonl',
            level=logging.DEBUG,
            format_type='json'
        )

        # Error logger with enhanced error tracking
        self.logger_error = self._create_logger(
            'LOG_ERROR',
            self.log_dir / 'error.log',
            level=logging.ERROR,
            format_type='enhanced'
        )

        # Performance logger for timing and metrics
        self.logger_perf = self._create_logger(
            'LOG_PERFORMANCE',
            self.log_dir / 'performance.jsonl',
            level=logging.INFO,
            format_type='json'
        )

        # Console logger for real-time feedback
        self.logger_console = self._create_console_logger()

    def _create_logger(self, name: str, file_path: Path, level: int, format_type: str) -> logging.Logger:
        """
        Create a logger with specified configuration.

        Args:
            name: Logger name
            file_path: Log file path
            level: Logging level
            format_type: Format type ('standard', 'json', 'enhanced')

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Clear existing handlers
        logger.handlers.clear()

        # Create rotating file handler (10MB max, 5 backups)
        handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )

        # Set formatter based on type
        if format_type == 'standard':
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        elif format_type == 'json':
            formatter = JsonFormatter()
        elif format_type == 'enhanced':
            formatter = EnhancedFormatter()

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _create_console_logger(self) -> logging.Logger:
        """Create console logger with colored output."""
        logger = logging.getLogger('LOG_CONSOLE')
        logger.setLevel(logging.INFO)
        logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)

        return logger

    # Core logging methods (compatible with existing V3 interface)
    def info(self, message: str, **kwargs):
        """Log info message to all appropriate loggers."""
        self._log_with_context(logging.INFO, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with enhanced error tracking."""
        self.operation_counters['errors'] += 1
        self._log_with_context(logging.ERROR, message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with detailed context."""
        self._log_with_context(logging.DEBUG, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)

    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log message with context to appropriate loggers."""

        # Enhance context with caller information
        frame = inspect.currentframe().f_back.f_back
        caller_info = {
            'function': frame.f_code.co_name,
            'line': frame.f_lineno,
            'file': os.path.basename(frame.f_code.co_filename)
        }

        # Merge context
        log_context = {**self.context, **caller_info, **kwargs}

        # Log to appropriate loggers based on level
        if level >= logging.ERROR:
            self.logger_error.error(message, extra=log_context)
            self.logger_console.error(f"❌ {message}")
        elif level >= logging.WARNING:
            self.logger_cr.warning(message)
            self.logger_console.warning(f"⚠️  {message}")
        elif level >= logging.INFO:
            self.logger_cr.info(message)
            self.logger_console.info(f"ℹ️  {message}")

        # Always log to detailed logger
        self.logger_detail.log(level, message, extra=log_context)

    # Performance tracking methods
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.operation_timers[operation] = time.time()

    def end_timer(self, operation: str, message: str = None):
        """End timing an operation and log performance."""
        if operation in self.operation_timers:
            duration = time.time() - self.operation_timers[operation]
            del self.operation_timers[operation]

            perf_data = {
                'operation': operation,
                'duration_ms': round(duration * 1000, 2),
                'timestamp': datetime.now().isoformat()
            }

            self.logger_perf.info(f"Performance: {operation}", extra=perf_data)

            if message:
                self.info(f"{message} (completed in {duration:.2f}s)")

    # Counter methods
    def increment_counter(self, counter_name: str, amount: int = 1):
        """Increment operation counter."""
        if counter_name in self.operation_counters:
            self.operation_counters[counter_name] += amount

    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        return {
            'release_name': self.release_name,
            'session_duration': time.time() - self.context['session_id'],
            'counters': self.operation_counters.copy(),
            'active_timers': list(self.operation_timers.keys())
        }

    # Context management
    def add_context(self, **kwargs):
        """Add context information to all future log messages."""
        self.context.update(kwargs)

    def log_session_summary(self):
        """Log a summary of the session."""
        stats = self.get_stats()

        summary = (
            f"SESSION SUMMARY for {self.release_name}:\n"
            f"  Duration: {stats['session_duration']:.2f} seconds\n"
            f"  API Calls: {stats['counters']['api_calls']}\n"
            f"  Template Operations: {stats['counters']['template_operations']}\n"
            f"  Phase Operations: {stats['counters']['phase_operations']}\n"
            f"  Variable Operations: {stats['counters']['variable_operations']}\n"
            f"  Errors: {stats['counters']['errors']}"
        )

        self.info(summary)
        self.logger_console.info(f"✅ {summary}")


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
        }

        # Add extra fields if present
        if hasattr(record, 'release_name'):
            log_entry['release_name'] = record.release_name
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'function'):
            log_entry['function'] = record.function
        if hasattr(record, 'line'):
            log_entry['line'] = record.line
        if hasattr(record, 'file'):
            log_entry['file'] = record.file

        # Add any additional context
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'message']:
                if not key.startswith('_'):
                    log_entry[key] = value

        return json.dumps(log_entry)


class EnhancedFormatter(logging.Formatter):
    """Enhanced formatter with detailed error information."""

    def format(self, record):
        # Base format
        base_msg = super().format(record)

        # Add caller information if available
        if hasattr(record, 'function') and hasattr(record, 'line'):
            caller_info = f" [{record.file}:{record.function}:{record.line}]"
            base_msg += caller_info

        # Add exception information if present
        if record.exc_info:
            base_msg += f"\nException: {record.exc_info[1]}"

        return base_msg


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = record.getMessage()
        return f"{color}{message}{self.RESET}"


# Convenience function for backward compatibility
def setup_enhanced_logger(release_name: str, log_directory: Optional[str] = None) -> XLRLogger:
    """
    Set up enhanced logger with backward compatibility.

    Args:
        release_name: Name of the release
        log_directory: Custom log directory

    Returns:
        Enhanced XLR logger instance
    """
    return XLRLogger(release_name, log_directory)