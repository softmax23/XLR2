"""
Logging utilities for XLR template creation
"""
import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    """Set up a logger with specified name and log file."""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def setup_logger_detail(name, log_file, level=logging.DEBUG):
    """Set up a detailed logger with debug level."""
    return setup_logger(name, log_file, level)

def setup_logger_error(name, log_file, level=logging.ERROR):
    """Set up an error logger."""
    return setup_logger(name, log_file, level)