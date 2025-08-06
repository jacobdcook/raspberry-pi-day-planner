"""
Utilities Module

This module provides helper functions and utilities for the Raspberry Pi Day Planner.
It includes time formatting, error handling, logging setup, and other common utilities.

Author: Raspberry Pi Day Planner
License: MIT
"""

import logging
import logging.handlers
import sys
import os
import signal
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Union
import traceback


def setup_logging(log_level: str = "INFO", 
                 log_file: Optional[str] = None,
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5) -> logging.Logger:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Path to log file (optional).
        max_bytes: Maximum size of log file before rotation.
        backup_count: Number of backup log files to keep.
        
    Returns:
        Configured logger instance.
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Create formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def handle_exit():
    """Setup signal handlers for graceful application exit."""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def format_time_delta(td: timedelta) -> str:
    """
    Format a timedelta object into a human-readable string.
    
    Args:
        td: Timedelta object to format.
        
    Returns:
        Formatted time string.
    """
    total_seconds = int(td.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds} seconds"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_time_until(target_time: datetime) -> str:
    """
    Format the time until a target datetime.
    
    Args:
        target_time: Target datetime.
        
    Returns:
        Formatted time string.
    """
    now = datetime.now()
    if target_time.tzinfo:
        now = now.replace(tzinfo=target_time.tzinfo)
    
    delta = target_time - now
    
    if delta.total_seconds() <= 0:
        return "Now"
    
    return format_time_delta(delta)


def format_time_since(past_time: datetime) -> str:
    """
    Format the time since a past datetime.
    
    Args:
        past_time: Past datetime.
        
    Returns:
        Formatted time string.
    """
    now = datetime.now()
    if past_time.tzinfo:
        now = now.replace(tzinfo=past_time.tzinfo)
    
    delta = now - past_time
    
    if delta.total_seconds() <= 0:
        return "Just now"
    
    return format_time_delta(delta)


def parse_time_string(time_str: str) -> Optional[datetime.time]:
    """
    Parse a time string into a time object.
    
    Args:
        time_str: Time string in various formats (HH:MM, HH:MM:SS, etc.).
        
    Returns:
        Time object or None if parsing fails.
    """
    try:
        # Try parsing with datetime
        dt = datetime.strptime(time_str, "%H:%M")
        return dt.time()
    except ValueError:
        try:
            # Try with seconds
            dt = datetime.strptime(time_str, "%H:%M:%S")
            return dt.time()
        except ValueError:
            return None


def format_priority(priority: int) -> str:
    """
    Format priority level into a human-readable string.
    
    Args:
        priority: Priority level (1-5).
        
    Returns:
        Formatted priority string.
    """
    priority_map = {
        1: "Critical",
        2: "High",
        3: "Medium",
        4: "Low",
        5: "Very Low"
    }
    return priority_map.get(priority, "Unknown")


def get_priority_color(priority: int) -> str:
    """
    Get color for priority level.
    
    Args:
        priority: Priority level (1-5).
        
    Returns:
        Color string.
    """
    color_map = {
        1: "red",
        2: "orange",
        3: "yellow",
        4: "lightblue",
        5: "lightgray"
    }
    return color_map.get(priority, "white")


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary.
    
    Args:
        dictionary: Dictionary to search.
        key: Key to look for.
        default: Default value if key not found.
        
    Returns:
        Value from dictionary or default.
    """
    return dictionary.get(key, default)


def validate_file_path(filepath: str, create_dir: bool = True) -> bool:
    """
    Validate if a file path is accessible and optionally create directory.
    
    Args:
        filepath: Path to validate.
        create_dir: Whether to create parent directory if it doesn't exist.
        
    Returns:
        True if path is valid, False otherwise.
    """
    try:
        path = Path(filepath)
        
        if create_dir:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        return True
    except Exception:
        return False


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        filepath: Path to the file.
        
    Returns:
        File size in megabytes.
    """
    try:
        size_bytes = Path(filepath).stat().st_size
        return round(size_bytes / (1024 * 1024), 2)
    except Exception:
        return 0.0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes.
        
    Returns:
        Formatted size string.
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def retry_on_error(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry a function on error.
    
    Args:
        func: Function to retry.
        max_retries: Maximum number of retries.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier for delay on each retry.
        
    Returns:
        Decorated function.
    """
    def wrapper(*args, **kwargs):
        last_exception = None
        current_delay = delay
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    time.sleep(current_delay)
                    current_delay *= backoff
                else:
                    raise last_exception
    
    return wrapper


def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    Log an exception with context.
    
    Args:
        logger: Logger instance.
        exception: Exception to log.
        context: Additional context string.
    """
    error_msg = f"{context}: {str(exception)}" if context else str(exception)
    logger.error(error_msg)
    logger.debug(f"Exception traceback: {traceback.format_exc()}")


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path.
        
    Returns:
        True if directory exists or was created, False otherwise.
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_system_info() -> Dict[str, str]:
    """
    Get basic system information.
    
    Returns:
        Dictionary containing system information.
    """
    import platform
    
    return {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }


def check_disk_space(path: str) -> Dict[str, Union[int, float]]:
    """
    Check available disk space for a path.
    
    Args:
        path: Path to check.
        
    Returns:
        Dictionary with disk space information.
    """
    try:
        import shutil
        total, used, free = shutil.disk_usage(path)
        
        return {
            'total_gb': round(total / (1024**3), 2),
            'used_gb': round(used / (1024**3), 2),
            'free_gb': round(free / (1024**3), 2),
            'free_percent': round((free / total) * 100, 2)
        }
    except Exception:
        return {
            'total_gb': 0,
            'used_gb': 0,
            'free_gb': 0,
            'free_percent': 0
        }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file system usage.
    
    Args:
        filename: Original filename.
        
    Returns:
        Sanitized filename.
    """
    import re
    
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized


def create_backup(filepath: str, backup_dir: Optional[str] = None) -> Optional[str]:
    """
    Create a backup of a file.
    
    Args:
        filepath: Path to the file to backup.
        backup_dir: Directory for backup (optional).
        
    Returns:
        Path to backup file or None if failed.
    """
    try:
        source_path = Path(filepath)
        if not source_path.exists():
            return None
        
        if backup_dir is None:
            backup_dir = source_path.parent / "backups"
        
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_filepath = backup_path / backup_filename
        
        # Copy file
        import shutil
        shutil.copy2(source_path, backup_filepath)
        
        return str(backup_filepath)
        
    except Exception:
        return None


def is_raspberry_pi() -> bool:
    """
    Check if running on a Raspberry Pi.
    
    Returns:
        True if running on Raspberry Pi, False otherwise.
    """
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except Exception:
        return False


def get_raspberry_pi_info() -> Dict[str, str]:
    """
    Get Raspberry Pi specific information.
    
    Returns:
        Dictionary with Raspberry Pi information.
    """
    if not is_raspberry_pi():
        return {}
    
    info = {}
    
    try:
        # Get model information
        with open('/proc/device-tree/model', 'r') as f:
            info['model'] = f.read().strip()
    except Exception:
        info['model'] = "Unknown"
    
    try:
        # Get CPU temperature
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read().strip()) / 1000.0
            info['cpu_temperature'] = f"{temp:.1f}°C"
    except Exception:
        info['cpu_temperature'] = "Unknown"
    
    return info 