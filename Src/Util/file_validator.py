# 16.05.24

import os
import errno
import platform
import unicodedata


# List of invalid characters for Windows filenames
WINDOWS_INVALID_CHARS = '<>:"/\\|?*'
WINDOWS_RESERVED_NAMES = [
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
]


# Invalid characters for macOS filenames
MACOS_INVALID_CHARS = '/:'


# Invalid characters for Linux/Android filenames
LINUX_INVALID_CHARS = '/\0'


# Maximum path length for Windows
WINDOWS_MAX_PATH = 260


def is_valid_filename(filename, system):
    """
    Validates if the given filename is valid for the specified system.

    Args:
        - filename (str): The filename to validate.
        - system (str): The operating system, e.g., 'Windows', 'Darwin' (macOS), or others for Linux/Android.

    Returns:
        bool: True if the filename is valid, False otherwise.
    """
    # Normalize Unicode
    filename = unicodedata.normalize('NFC', filename)
    
    # Common checks across all systems
    if filename.endswith(' ') or filename.endswith('.') or filename.endswith('/'):
        return False
    
    if filename.startswith('.') and system == "Darwin":
        return False
    
    # System-specific checks
    if system == "Windows":
        if len(filename) > WINDOWS_MAX_PATH:
            return False
        if any(char in filename for char in WINDOWS_INVALID_CHARS):
            return False
        name, ext = os.path.splitext(filename)
        if name.upper() in WINDOWS_RESERVED_NAMES:
            return False
    elif system == "Darwin":  # macOS
        if any(char in filename for char in MACOS_INVALID_CHARS):
            return False
    else:  # Linux and Android
        if any(char in filename for char in LINUX_INVALID_CHARS):
            return False
    
    return True


def can_create_file(file_path):
    """
    Checks if a file can be created at the given file path.

    Args:
        - file_path (str): The path where the file is to be created.

    Returns:
        bool: True if the file can be created, False otherwise.
    """
    current_system = platform.system()
    
    if not is_valid_filename(os.path.basename(file_path), current_system):
        return False
    
    try:
        with open(file_path, 'w') as file:
            pass
        os.remove(file_path)  # Cleanup if the file was created
        return True
    except OSError as e:
        if e.errno in (errno.EACCES, errno.ENOENT, errno.EEXIST, errno.ENOTDIR):
            return False
        raise  
