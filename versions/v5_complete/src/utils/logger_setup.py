"""
Logger Setup utilities for XLR Template Creator V5.

This module provides enhanced logging setup with multiple loggers
for different types of information (creation, details, errors).
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with file and console handlers.

    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def setup_logger_detail(name: str, log_file: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Set up a detailed logger for verbose information.

    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Detailed formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler only for detailed logs
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def setup_logger_error(name: str, log_file: str, level: int = logging.ERROR) -> logging.Logger:
    """
    Set up an error logger.

    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Error formatter with more details
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - ERROR - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler for errors (so they're immediately visible)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('ERROR: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def setup_rotating_logger(
    name: str,
    log_file: str,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Set up a logger with rotating file handler.

    Args:
        name: Logger name
        log_file: Path to log file
        max_bytes: Maximum bytes per log file
        backup_count: Number of backup files to keep
        level: Logging level

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger_stats(logger_name: str) -> dict:
    """
    Get statistics about a logger.

    Args:
        logger_name: Name of the logger

    Returns:
        Dictionary with logger statistics
    """
    logger = logging.getLogger(logger_name)

    stats = {
        'name': logger_name,
        'level': logger.level,
        'level_name': logging.getLevelName(logger.level),
        'handler_count': len(logger.handlers),
        'handlers': []
    }

    for handler in logger.handlers:
        handler_info = {
            'type': type(handler).__name__,
            'level': handler.level,
            'level_name': logging.getLevelName(handler.level)
        }

        if hasattr(handler, 'baseFilename'):
            handler_info['filename'] = handler.baseFilename

        stats['handlers'].append(handler_info)

    return stats