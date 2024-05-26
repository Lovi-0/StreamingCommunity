# 24.01.24

import re
import os
import time
import json
import shutil
import hashlib
import logging
import zipfile
import platform

from typing import List


# Variable
special_chars_to_remove = [
    '!', 
    '@', 
    '#', 
    '$', 
    '%', 
    '^', 
    '&', 
    '*', 
    '(', 
    ')', 
    '[', 
    ']', 
    '{', 
    '}', 
    '<', 
    '|', 
    '`',
    '~', 
    "'", 
    '"', 
    ';', 
    ':', 
    ',', 
    '?',
    "\\",
    "/"
]


def get_max_length_by_os(system: str) -> int:
    """
    Determines the maximum length for a base name based on the operating system.

    Args:
        system (str): The operating system name.

    Returns:
        int: The maximum length for the base name.
    """
    if system == 'windows':
        return 255  # NTFS and other common Windows filesystems support 255 characters for filenames
    elif system == 'darwin':  # macOS
        return 255  # HFS+ and APFS support 255 characters for filenames
    elif system == 'linux':
        return 255  # Most Linux filesystems (e.g., ext4) support 255 characters for filenames
    else:
        raise ValueError(f"Unsupported operating system: {system}")

def reduce_base_name(base_name: str) -> str:
    """
    Splits the file path into folder and base name, and reduces the base name based on the operating system.

    Args:
        base_name (str): The name of the file.

    Returns:
        str: The reduced base name.
    """

    
    # Determine the operating system
    system = platform.system().lower()
    
    # Get the maximum length for the base name based on the operating system
    max_length = get_max_length_by_os(system)
    
    # Reduce the base name if necessary
    if len(base_name) > max_length:
        if system == 'windows':
            # For Windows, truncate and add a suffix if needed
            base_name = base_name[:max_length - 3] + '___'
        elif system == 'darwin':  # macOS
            # For macOS, truncate without adding suffix
            base_name = base_name[:max_length]
        elif system == 'linux':
            # For Linux, truncate and add a numeric suffix if needed
            base_name = base_name[:max_length - 2] + '___'
    
    return base_name


def create_folder(folder_name: str) -> None:
    """
    Create a directory if it does not exist, and log the result.

    Args:
        folder_name (str): The path of the directory to be created.

    """
    try:

        logging.info(f"Try create folder: {folder_name}")
        os.makedirs(folder_name, exist_ok=True)
        
        if os.path.exists(folder_name) and os.path.isdir(folder_name):
            logging.info(f"Directory successfully created or already exists: {folder_name}")
        else:
            logging.error(f"Failed to create directory: {folder_name}")

    except OSError as e:
        logging.error(f"OS error occurred while creating the directory {folder_name}: {e}")
        raise
    
    except Exception as e:
        logging.error(f"An unexpected error occurred while creating the directory {folder_name}: {e}")
        raise

def check_file_existence(file_path):
    """
    Check if a file exists at the given file path.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    try:
        logging.info(f"Check if file exists: {file_path}")
        if os.path.exists(file_path):
            logging.info(f"The file '{file_path}' exists.")
            return True
        
        else:
            logging.warning(f"The file '{file_path}' does not exist.")
            return False
        
    except Exception as e:
        logging.error(f"An error occurred while checking file existence: {e}")
        return False

def remove_folder(folder_path: str) -> None:
    """
    Remove a folder if it exists.

    Args:
        - folder_path (str): The path to the folder to be removed.
    """

    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except OSError as e:
            print(f"Error removing folder '{folder_path}': {e}")


def remove_file(file_path: str) -> None:
    """
    Remove a file if it exists

    Args:
        - file_path (str): The path to the file to be removed.
    """
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error removing file '{file_path}': {e}")


def remove_special_characters(input_string):
    """
    Remove specified special characters from a string.

    Args:
        - input_string (str): The input string containing special characters.
        - special_chars (list): List of special characters to be removed.

    Returns:
        str: A new string with specified special characters removed.
    """
    # Compile regular expression pattern to match special characters
    pattern = re.compile('[' + re.escape(''.join(special_chars_to_remove)) + ']')

    # Use compiled pattern to replace special characters with an empty string
    cleaned_string = pattern.sub('', input_string)

    return cleaned_string


def move_file_one_folder_up(file_path) -> None:
    """
    Move a file one folder up from its current location.

    Args:
        - file_path (str): Path to the file to be moved.
    """
    
    # Get the directory of the file
    file_directory = os.path.dirname(file_path)

    # Get the parent directory
    parent_directory = os.path.dirname(file_directory)

    # Get the filename
    filename = os.path.basename(file_path)

    # New path for the file one folder up
    new_path = os.path.join(parent_directory, filename)

    # Move the file
    os.rename(file_path, new_path)


def delete_files_except_one(folder_path: str, keep_file: str) -> None:
    """
    Delete all files in a folder except for one specified file.

    Args:
        - folder_path (str): The path to the folder containing the files.
        - keep_file (str): The filename to keep in the folder.
    """

    try:

        # List all files in the folder
        files_in_folder = os.listdir(folder_path)
        
        # Iterate over each file in the folder
        for file_name in files_in_folder:
            file_path = os.path.join(folder_path, file_name)
            
            # Check if the file is not the one to keep and is a regular file
            if file_name != keep_file and os.path.isfile(file_path):
                os.remove(file_path)  # Delete the file

    except Exception as e:
        logging.error(f"An error occurred: {e}")


def decompress_file(downloaded_file_path: str, destination: str) -> None:
    """
    Decompress one file.

    Args:
        - downloaded_file_path (str): The path to the downloaded file.
        - destination (str): The directory where the file will be decompressed.
    """
    try:
        with zipfile.ZipFile(downloaded_file_path) as zip_file:
            zip_file.extractall(destination)
    except Exception as e:
        logging.error(f"Error decompressing file: {e}")
        raise


def read_json(path: str):
    """Reads JSON file and returns its content.

    Args:
        - path (str): The file path of the JSON file to read.

    Returns:
        variable: The content of the JSON file as a dictionary.
    """
    
    with open(path, "r") as file:
        config = json.load(file)

    return config


def save_json(json_obj, path: str) -> None:
    """Saves JSON object to the specified file path.

    Args:
        - json_obj (Dict[str, Any]): The JSON object to be saved.
        - path (str): The file path where the JSON object will be saved.
    """
    
    with open(path, 'w') as file:
        json.dump(json_obj, file, indent=4)  # Adjust the indentation as needed


def clean_json(path: str) -> None:
    """Reads JSON data from the file, cleans it, and saves it back.

    Args:
        - path (str): The file path of the JSON file to clean.
    """

    data = read_json(path)

    # Recursively replace all values with an empty string
    def recursive_empty_string(obj):
        if isinstance(obj, dict):
            return {key: recursive_empty_string(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [recursive_empty_string(item) for item in obj]
        else:
            return ""

    modified_data = recursive_empty_string(data)

    # Save the modified JSON data back to the file
    save_json(modified_data, path)


def format_size(size_bytes: float) -> str:
    """
    Format the size in bytes into a human-readable format.

    Args:
        - size_bytes (float): The size in bytes to be formatted.

    Returns:
        str: The formatted size.
    """

    if size_bytes <= 0:
        return "0B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0

    # Convert bytes to appropriate unit
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1

    # Round the size to two decimal places and return with the appropriate unit
    return f"{size_bytes:.2f} {units[unit_index]}"


def compute_sha1_hash(input_string: str) -> str:
    """
    Computes the SHA-1 hash of the input string.

    Args:
        - input_string (str): The string to be hashed.

    Returns:
        str: The SHA-1 hash of the input string.
    """
    # Compute the SHA-1 hash
    hashed_string = hashlib.sha1(input_string.encode()).hexdigest()
    
    # Return the hashed string
    return hashed_string


def decode_bytes(bytes_data: bytes, encodings_to_try: List[str] = None) -> str:
    """
    Decode a byte sequence using a list of encodings and return the decoded string.

    Args:
        - bytes_data (bytes): The byte sequence to decode.
        - encodings_to_try (List[str], optional): A list of encoding names to try for decoding.
            If None, defaults to ['utf-8', 'latin-1', 'ascii'].

    Returns:
        str or None: The decoded string if successful, None if decoding fails.
    """
    if encodings_to_try is None:
        encodings_to_try = ['utf-8', 'latin-1', 'ascii']

    for encoding in encodings_to_try:
        try:
            # Attempt decoding with the current encoding
            string_data = bytes_data.decode(encoding)
            logging.info("Decoded successfully with encoding: %s", encoding)
            logging.info("Decoded string: %s", string_data)
            return string_data
        except UnicodeDecodeError:
            continue  # Try the next encoding if decoding fails

    # If none of the encodings work, treat it as raw bytes
    logging.warning("Unable to decode the data as text. Treating it as raw bytes.")
    logging.info("Raw byte data: %s", bytes_data)
    return None


def convert_to_hex(bytes_data: bytes) -> str:
    """
    Convert a byte sequence to its hexadecimal representation.

    Args:
        - bytes_data (bytes): The byte sequence to convert.

    Returns:
        str: The hexadecimal representation of the byte sequence.
    """
    hex_data = ''.join(['{:02x}'.format(char) for char in bytes_data])
    logging.info("Hexadecimal representation of the data: %s", hex_data)
    return hex_data