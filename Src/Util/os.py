# 24.01.24

import re
import io
import os
import sys
import ssl
import time
import json
import errno
import shutil
import hashlib
import logging
import zipfile
import platform
import importlib
import subprocess
import contextlib
import urllib.request
import importlib.metadata

from typing import List


# External library
import httpx
import unicodedata


# Internal utilities
from .console import console
from .headers import get_headers



# --> OS FILE ASCII
special_chars_to_remove = [
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '{', '}', '<', 
    '>', '|', '`', '~', "'", '"', ';', ':', ',', '?', '\\', '/', '\t', ' ', '=', 
    '+', '\n', '\r', '\0'
]



def get_max_length_by_os(system: str) -> int:
    """
    Determines the maximum length for a base name based on the operating system.

    Parameters:
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

    Parameters:
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

def remove_special_characters(input_string):
    """
    Remove specified special characters from a string.

    Parameters:
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



# --> OS MANAGE OUTPUT
@contextlib.contextmanager
def suppress_output():
    with contextlib.redirect_stdout(io.StringIO()):
        yield



# --> OS MANAGE FOLDER 
def create_folder(folder_name: str) -> None:
    """
    Create a directory if it does not exist, and log the result.

    Parameters:
        folder_name (str): The path of the directory to be created.
    """

    if platform.system() == 'Windows':
        max_path_length = 260
    else:
        max_path_length = 4096

    try:
        logging.info(f"Try create folder: {folder_name}")
        
        # Check if path length exceeds the maximum allowed
        if len(folder_name) > max_path_length:
            logging.error(f"Path length exceeds the maximum allowed limit: {len(folder_name)} characters (Max: {max_path_length})")
            raise OSError(f"Path length exceeds the maximum allowed limit: {len(folder_name)} characters (Max: {max_path_length})")

        os.makedirs(folder_name, exist_ok=True)
        
        if os.path.exists(folder_name) and os.path.isdir(folder_name):
            logging.info(f"Directory successfully created or already exists: {folder_name}")
        else:
            logging.error(f"Failed to create directory: {folder_name}")

    except Exception as e:
        logging.error(f"An unexpected error occurred while creating the directory {folder_name}: {e}")
        raise

def check_file_existence(file_path):
    """
    Check if a file exists at the given file path.

    Parameters:
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

    Parameters:
        - folder_path (str): The path to the folder to be removed.
    """

    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except OSError as e:
            print(f"Error removing folder '{folder_path}': {e}")

def delete_files_except_one(folder_path: str, keep_file: str) -> None:
    """
    Delete all files in a folder except for one specified file.

    Parameters:
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



# --> OS MANAGE SIZE FILE AND INTERNET SPEED
def format_file_size(size_bytes: float) -> str:
    """
    Formats a file size from bytes into a human-readable string representation.

    Parameters:
        size_bytes (float): Size in bytes to be formatted.

    Returns:
        str: Formatted string representing the file size with appropriate unit (B, KB, MB, GB, TB).
    """
    if size_bytes <= 0:
        return "0B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0

    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1

    return f"{size_bytes:.2f} {units[unit_index]}"

def format_transfer_speed(bytes: float) -> str:
    """
    Formats a transfer speed from bytes per second into a human-readable string representation.

    Parameters:
        bytes (float): Speed in bytes per second to be formatted.

    Returns:
        str: Formatted string representing the transfer speed with appropriate unit (Bytes/s, KB/s, MB/s).
    """
    if bytes < 1024:
        return f"{bytes:.2f} Bytes/s"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.2f} KB/s"
    else:
        return f"{bytes / (1024 * 1024):.2f} MB/s"



# --> OS MANAGE KEY AND IV HEX
def compute_sha1_hash(input_string: str) -> str:
    """
    Computes the SHA-1 hash of the input string.

    Parameters:
        - input_string (str): The string to be hashed.

    Returns:
        str: The SHA-1 hash of the input string.
    """
    # Compute the SHA-1 hash
    hashed_string = hashlib.sha1(input_string.encode()).hexdigest()
    
    # Return the hashed string
    return hashed_string



# --> OS GET SUMMARY
def check_internet():
    while True:
        try:
            # Attempt to open a connection to a website to check for internet connection
            urllib.request.urlopen("https://www.google.com", timeout=3)
            console.log("[bold green]Internet is available![/bold green]")
            break

        except urllib.error.URLError:
            console.log("[bold red]Internet is not available. Waiting...[/bold red]")
            time.sleep(5)
    print()

def get_executable_version(command):
    try:
        version_output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode().split('\n')[0]
        return version_output.split(" ")[2]
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"{command[0]} not found")
        sys.exit(0)

def get_library_version(lib_name):
    try:
        version = importlib.metadata.version(lib_name)
        return f"{lib_name}-{version}"
    except importlib.metadata.PackageNotFoundError:
        return f"{lib_name}-not installed"

def get_system_summary():
    
    check_internet()
    console.print("[bold blue]System Summary[/bold blue][white]:")

    # Python version and platform
    python_version = sys.version.split()[0]
    python_implementation = platform.python_implementation()
    arch = platform.machine()
    os_info = platform.platform()
    openssl_version = ssl.OPENSSL_VERSION
    glibc_version = 'glibc ' + '.'.join(map(str, platform.libc_ver()[1]))
    
    console.print(f"[cyan]Python[white]: [bold red]{python_version} ({python_implementation} {arch}) - {os_info} ({openssl_version}, {glibc_version})[/bold red]")
    logging.info(f"Python: {python_version} ({python_implementation} {arch}) - {os_info} ({openssl_version}, {glibc_version})")
    
    # ffmpeg and ffprobe versions
    ffmpeg_version = get_executable_version(['ffmpeg', '-version'])
    ffprobe_version = get_executable_version(['ffprobe', '-version'])

    console.print(f"[cyan]Exe versions[white]: [bold red]ffmpeg {ffmpeg_version}, ffprobe {ffprobe_version}[/bold red]")
    logging.info(f"Exe versions: ffmpeg {ffmpeg_version}, ffprobe {ffprobe_version}")

    # Optional libraries versions
    optional_libraries = [line.strip() for line in open('requirements.txt', 'r', encoding='utf-8-sig')]
    optional_libs_versions = [get_library_version(lib) for lib in optional_libraries]
    
    console.print(f"[cyan]Libraries[white]: [bold red]{', '.join(optional_libs_versions)}[/bold red]\n")
    logging.info(f"Libraries: {', '.join(optional_libs_versions)}")



# --> OS MANAGE NODE JS 
def is_node_installed() -> bool:
    """
    Checks if Node.js is installed on the system.

    Returns:
        bool: True if Node.js is installed, False otherwise.
    """
    try:
        # Run the command 'node -v' to get the Node.js version
        result = subprocess.run(['node', '-v'], capture_output=True, text=True, check=True)

        # If the command runs successfully and returns a version number, Node.js is installed
        if result.stdout.startswith('v'):
            return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If there is an error running the command or the command is not found, Node.js is not installed
        return False

    return False

def run_node_script(script_content: str) -> str:
    """
    Runs a Node.js script and returns its output.

    Parameters:
        script_content (str): The content of the Node.js script to run.

    Returns:
        str: The output of the Node.js script.
    """

    # Check if Node.js is installed
    if not is_node_installed():
        raise EnvironmentError("Node.js is not installed on the system.")

    # Write the script content to a temporary file
    with open('script.js', 'w') as file:
        file.write(script_content)

    try:
        # Run the Node.js script using subprocess and capture the output
        result = subprocess.run(['node', 'script.js'], capture_output=True, text=True, check=True)
        return result.stdout
    
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running Node.js script: {e.stderr}")
    
    finally:
        # Clean up the temporary script file
        import os
        os.remove('script.js')

def run_node_script_api(script_content: str) -> str:
    """
    Runs a Node.js script and returns its output.

    Parameters:
        script_content (str): The content of the Node.js script to run.

    Returns:
        str: The output of the Node.js script.
    """

    headers = {
        'accept': '*/*',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'dnt': '1',
        'origin': 'https://onecompiler.com',
        'priority': 'u=1, i',
        'referer': 'https://onecompiler.com/javascript',
        'user-agent': get_headers()
    }

    json_data = {
        'name': 'JavaScript',
        'title': '42gyum6qn',
        'version': 'ES6',
        'mode': 'javascript',
        'description': None,
        'extension': 'js',
        'languageType': 'programming',
        'active': False,
        'properties': {
            'language': 'javascript',
            'docs': False,
            'tutorials': False,
            'cheatsheets': False,
            'filesEditable': False,
            'filesDeletable': False,
            'files': [
                {
                    'name': 'index.js',
                    'content': script_content
                },
            ],
            'newFileOptions': [
                {
                    'helpText': 'New JS file',
                    'name': 'script${i}.js',
                    'content': "/**\n *  In main file\n *  let script${i} = require('./script${i}');\n *  console.log(script${i}.sum(1, 2));\n */\n\nfunction sum(a, b) {\n    return a + b;\n}\n\nmodule.exports = { sum };",
                },
                {
                    'helpText': 'Add Dependencies',
                    'name': 'package.json',
                    'content': '{\n  "name": "main_app",\n  "version": "1.0.0",\n  "description": "",\n  "main": "HelloWorld.js",\n  "dependencies": {\n    "lodash": "^4.17.21"\n  }\n}',
                },
            ],
        },
        '_id': '42gcvpkbg_42gyuud7m',
        'user': None,
        'visibility': 'public',
    }

    # Return error
    response = httpx.post('https://onecompiler.com/api/code/exec', headers=headers, json=json_data, timeout=15)
    response.raise_for_status()

    if response.status_code == 200:
        return str(response.json()['stderr']).split("\n")[1]
    
    else:
        logging.error("Cant connect to site: onecompiler.com")
        sys.exit(0)




# --> OS FILE VALIDATOR

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

    Parameters:
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

    Parameters:
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
