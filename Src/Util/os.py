# 24.01.24

import shutil
import os
import time
import json
import hashlib
import logging
import re


def remove_folder(folder_path: str) -> None:
    """
    Remove a folder if it exists.

    Parameters:
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

    Parameters:
    - file_path (str): The path to the file to be removed.
    """
    
    if os.path.exists(file_path):
        time.sleep(1)

        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error removing file '{file_path}': {e}")


def remove_special_characters(filename) -> str:
    """
    Removes special characters from a filename to make it suitable for creating a filename in Windows.
    
    Args:
        filename (str): The original filename containing special characters.
    
    Returns:
        str: The cleaned filename without special characters.
    """

    # Define the regex pattern to match special characters
    pattern = r'[^\w\-_\. ]'
    
    # Replace special characters with an empty string
    cleaned_filename = re.sub(pattern, '', filename)
    
    return cleaned_filename


def move_file_one_folder_up(file_path) -> None:
    """
    Move a file one folder up from its current location.

    Args:
        file_path (str): Path to the file to be moved.
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


def read_json(path: str):
    """Reads JSON file and returns its content.

    Args:
        path (str): The file path of the JSON file to read.

    Returns:
        variable: The content of the JSON file as a dictionary.
    """
    
    with open(path, "r") as file:
        config = json.load(file)

    return config


def save_json(json_obj, path: str) -> None:
    """Saves JSON object to the specified file path.

    Args:
        json_obj (Dict[str, Any]): The JSON object to be saved.
        path (str): The file path where the JSON object will be saved.
    """
    
    with open(path, 'w') as file:
        json.dump(json_obj, file, indent=4)  # Adjust the indentation as needed


def clean_json(path: str) -> None:
    """Reads JSON data from the file, cleans it, and saves it back.

    Args:
        path (str): The file path of the JSON file to clean.
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
        size_bytes (float): The size in bytes to be formatted.

    Returns:
        str: The formatted size.
    """

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
    input_string (str): The string to be hashed.

    Returns:
    str: The SHA-1 hash of the input string.
    """
    # Compute the SHA-1 hash
    hashed_string = hashlib.sha1(input_string.encode()).hexdigest()
    
    # Return the hashed string
    return hashed_string


def decode_bytes(bytes_data: bytes, encodings_to_try: list[str] = None) -> str:
    """
    Decode a byte sequence using a list of encodings and return the decoded string.

    Args:
        bytes_data (bytes): The byte sequence to decode.
        encodings_to_try (List[str], optional): A list of encoding names to try for decoding.
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
        bytes_data (bytes): The byte sequence to convert.

    Returns:
        str: The hexadecimal representation of the byte sequence.
    """
    hex_data = ''.join(['{:02x}'.format(char) for char in bytes_data])
    logging.info("Hexadecimal representation of the data: %s", hex_data)
    return hex_data