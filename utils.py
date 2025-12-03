"""
Utility functions for blockchain file storage system.
"""

import base64
import time
from datetime import datetime


def encode_file_to_base64(file_bytes):
    """
    Encode file bytes to Base64 string.
    
    Args:
        file_bytes (bytes): Raw file bytes
        
    Returns:
        str: Base64 encoded string
    """
    return base64.b64encode(file_bytes).decode('utf-8')


def decode_base64_to_file(base64_string):
    """
    Decode Base64 string back to file bytes.
    
    Args:
        base64_string (str): Base64 encoded string
        
    Returns:
        bytes: Original file bytes
    """
    return base64.b64decode(base64_string)


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_timestamp(timestamp):
    """
    Format Unix timestamp to human-readable date/time.
    
    Args:
        timestamp (float): Unix timestamp
        
    Returns:
        str: Formatted datetime string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_current_timestamp():
    """
    Get current Unix timestamp.
    
    Returns:
        float: Current timestamp
    """
    return time.time()


def validate_file_data(file_data):
    """
    Validate file transaction data.
    
    Args:
        file_data (dict): File transaction data
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ["user", "v_file", "file_data", "file_size"]
    
    for field in required_fields:
        if field not in file_data:
            return False, f"Missing required field: {field}"
    
    # Validate file_size is a number
    try:
        int(file_data["file_size"])
    except (ValueError, TypeError):
        return False, "file_size must be a valid number"
    
    return True, None


def truncate_string(s, max_length=50):
    """
    Truncate string to maximum length with ellipsis.
    
    Args:
        s (str): String to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length-3] + "..."
