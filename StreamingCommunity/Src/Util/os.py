# 24.01.24

import io
import os
import sys
import ssl
import time
import shutil
import hashlib
import logging
import platform
import unidecode
import importlib
import subprocess
import contextlib
import pathvalidate
import urllib.request
import importlib.metadata


# External library
import httpx


# Internal utilities
from StreamingCommunity.Src.Util.console import console


# Variable
OS_CONFIGURATIONS = {
        'windows': {
            'max_length': 255,
            'invalid_chars': '<>:"/\\|?*',
            'reserved_names': [
                "CON", "PRN", "AUX", "NUL",
                "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
            ],
            'max_path': 255
        },
        'darwin': {
            'max_length': 4096,
            'invalid_chars': '/:',
            'reserved_names': [],
            'hidden_file_restriction': True
        },
        'linux': {
            'max_length': 4096,
            'invalid_chars': '/\0',
            'reserved_names': []
        }
    }



class OsManager:
    def __init__(self):
        self.system = self._detect_system()
        self.config = OS_CONFIGURATIONS.get(self.system, {})

    def _detect_system(self) -> str:
        """Detect and normalize operating system name."""
        system = platform.system().lower()

        if system in OS_CONFIGURATIONS:
            return system
        
        raise ValueError(f"Unsupported operating system: {system}")

    def _process_filename(self, filename: str) -> str:
        """
        Comprehensively process filename with cross-platform considerations.
        
        Args:
            filename (str): Original filename.
        
        Returns:
            str: Processed filename.
        """
        # Preserve file extension
        logging.info("_process_filename: ", filename)
        name, ext = os.path.splitext(filename)
        
        # Handle length restrictions
        if len(name) > self.config['max_length']:
            name = self._truncate_filename(name)
        
        # Reconstruct filename
        processed_filename = name + ext
        
        return processed_filename

    def _truncate_filename(self, name: str) -> str:
        """
        Truncate filename based on OS-specific rules.
        
        Args:
            name (str): Original filename.
        
        Returns:
            str: Truncated filename.
        """
        logging.info("_truncate_filename: ", name)

        if self.system == 'windows':
            return name[:self.config['max_length'] - 3] + '___'
        elif self.system == 'darwin':
            return name[:self.config['max_length']]
        elif self.system == 'linux':
            return name[:self.config['max_length'] - 2] + '___'

    def get_sanitize_file(self, filename: str) -> str:
        """
        Sanitize filename using pathvalidate with unidecode.
        
        Args:
            filename (str): Original filename.
        
        Returns:
            str: Sanitized filename.
        """
        logging.info("get_sanitize_file: ", filename)

        # Decode unicode characters and sanitize
        decoded_filename = unidecode.unidecode(filename)
        sanitized_filename = pathvalidate.sanitize_filename(decoded_filename)
        
        # Truncate if necessary based on OS configuration
        name, ext = os.path.splitext(sanitized_filename)
        if len(name) > self.config['max_length']:
            name = self._truncate_filename(name)
        
        logging.info("return :", name + ext)
        return name + ext

    def get_sanitize_path(self, path: str) -> str:
        """
        Sanitize folder path using pathvalidate with unidecode.
        
        Args:
            path (str): Original folder path.
        
        Returns:
            str: Sanitized folder path.
        """
        logging.info("get_sanitize_file: ", path)

        # Decode unicode characters and sanitize
        decoded_path = unidecode.unidecode(path)
        sanitized_path = pathvalidate.sanitize_filepath(decoded_path)
        
        # Split path and process each component
        path_components = os.path.normpath(sanitized_path).split(os.sep)
        processed_components = []
        
        for component in path_components:
            # Truncate component if necessary
            if len(component) > self.config['max_length']:
                component = self._truncate_filename(component)
            processed_components.append(component)

        logging.info("return :", os.path.join(*processed_components))
        return os.path.join(*processed_components)

    def create_path(self, path: str, mode: int = 0o755) -> bool:
        """
        Create directory path with specified permissions.
        
        Args:
            path (str): Path to create.
            mode (int, optional): Directory permissions. Defaults to 0o755.
        
        Returns:
            bool: True if path created successfully, False otherwise.
        """
        try:
            # Sanitize path first
            sanitized_path = self.get_sanitize_path(path)
            
            # Create directory with recursive option
            os.makedirs(sanitized_path, mode=mode, exist_ok=True)
            return True
        
        except Exception as e:
            logging.error(f"Path creation error: {e}")
            return False

    def remove_folder(self, folder_path: str) -> bool:
        """
        Safely remove a folder.
        
        Args:
            folder_path (str): Path of directory to remove.
        
        Returns:
            bool: Removal status.
        """
        try:
            shutil.rmtree(folder_path)
            return True
        except OSError as e:
            logging.error(f"Folder removal error: {e}")
            return False
    
    def remove_files_except_one(self, folder_path: str, keep_file: str) -> None:
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
            raise
    
    def check_file(self, file_path: str) -> bool:
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
                return False
            
        except Exception as e:
            logging.error(f"An error occurred while checking file existence: {e}")
            return False


class InternManager():

    def format_file_size(self, size_bytes: float) -> str:
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

    def format_transfer_speed(self, bytes: float) -> str:
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

    @staticmethod
    def check_internet():
        while True:
            try:
                httpx.get("https://www.google.com")
                console.log("[bold green]Internet is available![/bold green]")
                break

            except urllib.error.URLError:
                console.log("[bold red]Internet is not available. Waiting...[/bold red]")
                time.sleep(5)

        print()


class OsSummary():

    def get_executable_version(self, command: list):
        """
        Get the version of a given command-line executable.

        Args:
            command (list): The command to run, e.g., `['ffmpeg', '-version']`.

        Returns:
            str: The version string of the executable.

        Raises:
            SystemExit: If the command is not found or fails to execute.
        """

        try:
            version_output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode().split('\n')[0]
            return version_output.split(" ")[2]
        
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"{command[0]} not found")
            sys.exit(0)

    def get_library_version(self, lib_name: str):
        """
        Retrieve the version of a Python library.

        Args:
            lib_name (str): The name of the Python library.

        Returns:
            str: The library name followed by its version, or `-not installed` if not found.
        """

        try:
            version = importlib.metadata.version(lib_name)
            return f"{lib_name}-{version}"
        
        except importlib.metadata.PackageNotFoundError:
            return f"{lib_name}-not installed"

    def get_system_summary(self):
        """
        Generate a summary of the system environment.

        Includes:
            - Python version and implementation details.
            - Operating system and architecture.
            - Versions of `ffmpeg` and `ffprobe` executables.
            - Installed Python libraries as listed in `requirements.txt`.
        """
        
        # Check internet connectivity
        InternManager().check_internet()
        console.print("[bold blue]System Summary[/bold blue][white]:")

        # Python version and platform
        python_version = sys.version.split()[0]
        python_implementation = platform.python_implementation()
        arch = platform.machine()
        os_info = platform.platform()
        glibc_version = 'glibc ' + '.'.join(map(str, platform.libc_ver()[1]))
        
        console.print(f"[cyan]Python[white]: [bold red]{python_version} ({python_implementation} {arch}) - {os_info} ({glibc_version})[/bold red]")
        logging.info(f"Python: {python_version} ({python_implementation} {arch}) - {os_info} ({glibc_version})")
        
        # ffmpeg and ffprobe versions
        ffmpeg_version = self.get_executable_version(['ffmpeg', '-version'])
        ffprobe_version = self.get_executable_version(['ffprobe', '-version'])

        console.print(f"[cyan]Exe versions[white]: [bold red]ffmpeg {ffmpeg_version}, ffprobe {ffprobe_version}[/bold red]")
        logging.info(f"Dependencies: ffmpeg {ffmpeg_version}, ffprobe {ffprobe_version}")

        # Optional libraries versions
        """optional_libraries = [line.strip() for line in open('requirements.txt', 'r', encoding='utf-8-sig')]
        optional_libs_versions = [self.get_library_version(lib) for lib in optional_libraries]
        
        console.print(f"[cyan]Libraries[white]: [bold red]{', '.join(optional_libs_versions)}[/bold red]\n")
        logging.info(f"Libraries: {', '.join(optional_libs_versions)}")"""



# OTHER
os_manager = OsManager()
internet_manager = InternManager()
os_summary = OsSummary()

@contextlib.contextmanager
def suppress_output():
    with contextlib.redirect_stdout(io.StringIO()):
        yield

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
