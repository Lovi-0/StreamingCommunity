# 24.01.2024

import os
import platform
import subprocess
import zipfile
import tarfile
import logging
import requests
import shutil
import glob
from typing import Optional, Tuple


# External library
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn


# Variable
console = Console()

# https://github.com/eugeneware/ffmpeg-static/releases
# https://github.com/GyanD/codexffmpeg/releases/
FFMPEG_CONFIGURATION = {
    'windows': {
        'base_dir': lambda home: os.path.join(os.path.splitdrive(home)[0] + os.path.sep, 'binary'),
        'download_url': 'https://github.com/GyanD/codexffmpeg/releases/download/{version}/ffmpeg-{version}-full_build.zip',
        'file_extension': '.zip',
        'executables': ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
    },
    'darwin': {
        'base_dir': lambda home: os.path.join(home, 'Applications', 'binary'),
        'download_url': 'https://github.com/eugeneware/ffmpeg-static/releases/download/b{version}/ffmpeg-macOS-{arch}.zip',
        'file_extension': '.zip',
        'executables': ['ffmpeg', 'ffprobe', 'ffplay']
    },
    'linux': {
        'base_dir': lambda home: os.path.join(home, '.local', 'bin', 'binary'),
        'download_url': 'https://github.com/eugeneware/ffmpeg-static/releases/download/b{version}/ffmpeg-linux-{arch}.tar.xz',
        'file_extension': '.tar.xz',
        'executables': ['ffmpeg', 'ffprobe', 'ffplay']
    }
}


class FFMPEGDownloader:
    """
    A class for downloading and managing FFmpeg executables.
    
    This class handles the detection of the operating system, downloading of FFmpeg binaries,
    and management of the FFmpeg executables (ffmpeg, ffprobe, and ffplay).

    Attributes:
        os_name (str): The detected operating system name
        arch (str): The system architecture (e.g., x86_64, arm64)
        home_dir (str): User's home directory path
        base_dir (str): Base directory for storing FFmpeg binaries
    """

    def __init__(self):
        self.os_name = self._detect_system()
        self.arch = self._detect_arch()
        self.home_dir = os.path.expanduser('~')
        self.base_dir = self._get_base_directory()

    def _detect_system(self) -> str:
        """
        Detect and normalize the operating system name.

        Returns:
            str: Normalized operating system name ('windows', 'darwin', or 'linux')

        Raises:
            ValueError: If the operating system is not supported
        """
        system = platform.system().lower()
        if system in FFMPEG_CONFIGURATION:
            return system
        raise ValueError(f"Unsupported operating system: {system}")

    def _detect_arch(self) -> str:
        """
        Detect and normalize the system architecture.

        Returns:
            str: Normalized architecture name (e.g., 'x86_64', 'arm64')
            
        The method normalizes various architecture names to consistent values:
            - amd64/x86_64/x64 -> x86_64
            - arm64/aarch64 -> arm64
        """
        machine = platform.machine().lower()
        arch_map = {
            'amd64': 'x86_64', 
            'x86_64': 'x86_64', 
            'x64': 'x86_64',
            'arm64': 'arm64', 
            'aarch64': 'arm64'
        }
        return arch_map.get(machine, machine)

    def _get_base_directory(self) -> str:
        """
        Get and create the base directory for storing FFmpeg binaries.

        Returns:
            str: Path to the base directory
            
        The directory location varies by operating system:
            - Windows: C:\\binary
            - macOS: ~/Applications/binary
            - Linux: ~/.local/bin/binary
        """
        base_dir = FFMPEG_CONFIGURATION[self.os_name]['base_dir'](self.home_dir)
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    def _check_existing_binaries(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Check if FFmpeg binaries already exist in the base directory.
        Enhanced to check both the binary directory and system paths on macOS.
        """
        config = FFMPEG_CONFIGURATION[self.os_name]
        executables = config['executables']
        found_executables = []

        # For macOS, check both binary directory and system paths
        if self.os_name == 'darwin':
            potential_paths = [
                '/usr/local/bin',
                '/opt/homebrew/bin',
                '/usr/bin',
                self.base_dir
            ]
            
            for executable in executables:
                found = None
                for path in potential_paths:
                    full_path = os.path.join(path, executable)
                    if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                        found = full_path
                        break
                found_executables.append(found)
        else:

            # Original behavior for other operating systems
            for executable in executables:
                exe_paths = glob.glob(os.path.join(self.base_dir, executable))
                found_executables.append(exe_paths[0] if exe_paths else None)

        return tuple(found_executables) if len(found_executables) == 3 else (None, None, None)

    def _get_latest_version(self, repo: str) -> Optional[str]:
        """
        Get the latest FFmpeg version from the GitHub releases page.

        Returns:
            Optional[str]: The latest version string, or None if retrieval fails.

        Raises:
            requests.exceptions.RequestException: If there are network-related errors.
        """
        try:
            # Use GitHub API to fetch the latest release
            response = requests.get(f'https://api.github.com/repos/{repo}/releases/latest')
            response.raise_for_status()
            latest_release = response.json()

            # Extract the tag name or version from the release
            return latest_release.get('tag_name')
        
        except Exception as e:
            logging.error(f"Unable to get version from GitHub: {e}")
            return None

    def _download_file(self, url: str, destination: str) -> bool:
        """
        Download a file from URL with a Rich progress bar display.

        Parameters:
            url (str): The URL to download the file from. Should be a direct download link.
            destination (str): Local file path where the downloaded file will be saved.

        Returns:
            bool: True if download was successful, False otherwise.

        Raises:
            requests.exceptions.RequestException: If there are network-related errors
            IOError: If there are issues writing to the destination file
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            with open(destination, 'wb') as file, \
                Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeRemainingColumn()
                ) as progress:
                
                download_task = progress.add_task("[green]Downloading FFmpeg", total=total_size)
                for chunk in response.iter_content(chunk_size=8192):
                    size = file.write(chunk)
                    progress.update(download_task, advance=size)
            return True
        except Exception as e:
            logging.error(f"Download error: {e}")
            return False

    def _extract_and_copy_binaries(self, archive_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract FFmpeg binaries from the downloaded archive and copy them to the base directory.

        Parameters:
            archive_path (str): Path to the downloaded archive file

        Returns:
            Tuple[Optional[str], Optional[str], Optional[str]]: Paths to the extracted ffmpeg, 
            ffprobe, and ffplay executables. Returns None for each executable that couldn't be extracted.
        """
        try:
            extraction_path = os.path.join(self.base_dir, 'temp_extract')
            os.makedirs(extraction_path, exist_ok=True)

            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extraction_path)
            elif archive_path.endswith('.tar.xz'):
                with tarfile.open(archive_path) as tar_ref:
                    tar_ref.extractall(extraction_path)

            config = FFMPEG_CONFIGURATION[self.os_name]
            executables = config['executables']
            found_paths = []

            for executable in executables:
                exe_paths = glob.glob(os.path.join(extraction_path, '**', executable), recursive=True)
                
                if exe_paths:
                    dest_path = os.path.join(self.base_dir, executable)
                    shutil.copy2(exe_paths[0], dest_path)
                    
                    if self.os_name != 'windows':
                        os.chmod(dest_path, 0o755)
                    
                    found_paths.append(dest_path)
                else:
                    found_paths.append(None)

            shutil.rmtree(extraction_path, ignore_errors=True)
            os.remove(archive_path)

            return tuple(found_paths) if len(found_paths) == 3 else (None, None, None)

        except Exception as e:
            logging.error(f"Extraction/copy error: {e}")
            return None, None, None

    def download(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Main method to download and set up FFmpeg executables.

        Returns:
            Tuple[Optional[str], Optional[str], Optional[str]]: Paths to ffmpeg, ffprobe, and ffplay executables.
            Returns None for each executable that couldn't be downloaded or set up.
        """
        existing_ffmpeg, existing_ffprobe, existing_ffplay = self._check_existing_binaries()
        if all([existing_ffmpeg, existing_ffprobe, existing_ffplay]):
            return existing_ffmpeg, existing_ffprobe, existing_ffplay

        repo = 'GyanD/codexffmpeg' if self._detect_system() == 'windows' else 'eugeneware/ffmpeg-static'
        console.print(f"[red]Use {repo} repo for downloading ffmpeg.")
        version = self._get_latest_version(repo)

        if not version:
            logging.error("Cannot proceed: version not found")
            return None, None, None

        config = FFMPEG_CONFIGURATION[self.os_name]
        download_url = config['download_url'].format(
            version=version, 
            arch=self.arch
        )
        
        download_path = os.path.join(
            self.base_dir, 
            f'ffmpeg-{version}{config["file_extension"]}'
        )
        
        console.print(f"[bold blue]Downloading FFmpeg from:[/] {download_url}")
        if not self._download_file(download_url, download_path):
            return None, None, None
        
        return self._extract_and_copy_binaries(download_path)

def check_ffmpeg() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Check for FFmpeg executables in the system and download them if not found.
    Enhanced detection for macOS systems.

    Returns:
        Tuple[Optional[str], Optional[str], Optional[str]]: Paths to ffmpeg, ffprobe, and ffplay executables.
    """
    try:
        system_platform = platform.system().lower()
        
        # Special handling for macOS
        if system_platform == 'darwin':

            # Common installation paths on macOS
            potential_paths = [
                '/usr/local/bin',                               # Homebrew default
                '/opt/homebrew/bin',                            # Apple Silicon Homebrew
                '/usr/bin',                                     # System default
                os.path.expanduser('~/Applications/binary'),    # Custom installation
                '/Applications/binary'                          # Custom installation
            ]
            
            for path in potential_paths:
                ffmpeg_path = os.path.join(path, 'ffmpeg')
                ffprobe_path = os.path.join(path, 'ffprobe')
                ffplay_path = os.path.join(path, 'ffplay')
                
                if (os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path) and 
                    os.access(ffmpeg_path, os.X_OK) and os.access(ffprobe_path, os.X_OK)):
                    
                    # Return found executables, with ffplay being optional
                    ffplay_path = ffplay_path if os.path.exists(ffplay_path) else None
                    return ffmpeg_path, ffprobe_path, ffplay_path

        # Windows detection
        elif system_platform == 'windows':
            try:
                ffmpeg_path = subprocess.check_output(
                    ['where', 'ffmpeg'], stderr=subprocess.DEVNULL, text=True
                ).strip().split('\n')[0]
                
                ffprobe_path = subprocess.check_output(
                    ['where', 'ffprobe'], stderr=subprocess.DEVNULL, text=True
                ).strip().split('\n')[0]
                
                ffplay_path = subprocess.check_output(
                    ['where', 'ffplay'], stderr=subprocess.DEVNULL, text=True
                ).strip().split('\n')[0]

                return ffmpeg_path, ffprobe_path, ffplay_path
            
            except subprocess.CalledProcessError:
                logging.warning("One or more FFmpeg binaries were not found with command where")

        # Linux detection
        else:
            ffmpeg_path = shutil.which('ffmpeg')
            ffprobe_path = shutil.which('ffprobe')
            ffplay_path = shutil.which('ffplay')
            
            if ffmpeg_path and ffprobe_path:
                return ffmpeg_path, ffprobe_path, ffplay_path

        # If executables were not found, attempt to download FFmpeg
        downloader = FFMPEGDownloader()
        return downloader.download()

    except Exception as e:
        logging.error(f"Error checking or downloading FFmpeg executables: {e}")
        return None, None, None