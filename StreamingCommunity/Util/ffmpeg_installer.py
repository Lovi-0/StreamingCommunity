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
FFMPEG_CONFIGURATION = {
    'windows': {
        'base_dir': lambda home: os.path.join(os.path.splitdrive(home)[0] + os.path.sep, 'binary'),
        'download_url': 'https://github.com/GyanD/codexffmpeg/releases/download/{version}/ffmpeg-{version}-full_build.zip',
        'file_extension': '.zip',
        'executables': ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
    },
    'darwin': {
        'base_dir': lambda home: os.path.join(home, 'Applications', 'binary'),
        'download_url': 'https://evermeet.cx/ffmpeg/ffmpeg-{version}.zip',
        'file_extension': '.zip',
        'executables': ['ffmpeg', 'ffprobe', 'ffplay']
    },
    'linux': {
        'base_dir': lambda home: os.path.join(home, '.local', 'bin', 'binary'),
        'download_url': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-{arch}-static.tar.xz',
        'file_extension': '.tar.xz',
        'executables': ['ffmpeg', 'ffprobe', 'ffplay']
    }
}



class FFMPEGDownloader:
    def __init__(self):
        self.os_name = self._detect_system()
        self.arch = self._detect_arch()
        self.home_dir = os.path.expanduser('~')
        self.base_dir = self._get_base_directory()

    def _detect_system(self) -> str:
        """Detect and normalize operating system name."""
        system = platform.system().lower()

        if system in FFMPEG_CONFIGURATION:
            return system
        
        raise ValueError(f"Unsupported operating system: {system}")

    def _detect_arch(self) -> str:
        """
        Detect system architecture
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
        Get base directory for binaries
        """
        base_dir = FFMPEG_CONFIGURATION[self.os_name]['base_dir'](self.home_dir)
        os.makedirs(base_dir, exist_ok=True)

        return base_dir

    def _check_existing_binaries(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Check if FFmpeg binaries already exist in the base directory
        """
        config = FFMPEG_CONFIGURATION[self.os_name]
        executables = config['executables']

        found_executables = []
        for executable in executables:
            
            # Search for exact executable in base directory
            exe_paths = glob.glob(os.path.join(self.base_dir, executable))
            if exe_paths:
                found_executables.append(exe_paths[0])

        # Return paths if both executables are found
        if len(found_executables) == len(executables):
            return tuple(found_executables)

        return None, None

    def _get_latest_version(self) -> str:
        """
        Get the latest FFmpeg version
        """
        try:
            version_url = 'https://www.gyan.dev/ffmpeg/builds/release-version'
            return requests.get(version_url).text.strip()
        
        except Exception as e:
            logging.error(f"Unable to get version: {e}")
            return None

    def _download_file(self, url: str, destination: str) -> bool:
        """
        Download with Rich progress bar
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

    def _extract_and_copy_binaries(self, archive_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract archive and copy executables to base directory
        """
        try:
            # Temporary extraction path
            extraction_path = os.path.join(self.base_dir, 'temp_extract')
            os.makedirs(extraction_path, exist_ok=True)

            # Extract based on file type
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extraction_path)
            elif archive_path.endswith('.tar.xz'):
                import lzma
                with lzma.open(archive_path, 'rb') as xz_file:
                    with tarfile.open(fileobj=xz_file) as tar_ref:
                        tar_ref.extractall(extraction_path)

            # Find and copy executables
            config = FFMPEG_CONFIGURATION[self.os_name]
            executables = config['executables']
            
            found_paths = []
            for executable in executables:
                # Find executable in extracted files
                exe_paths = glob.glob(os.path.join(extraction_path, '**', executable), recursive=True)
                
                if exe_paths:
                    # Copy to base directory
                    dest_path = os.path.join(self.base_dir, executable)
                    shutil.copy2(exe_paths[0], dest_path)
                    
                    # Set execution permissions for Unix-like systems
                    if self.os_name != 'windows':
                        os.chmod(dest_path, 0o755)
                    
                    found_paths.append(dest_path)

            # Clean up temporary extraction directory
            shutil.rmtree(extraction_path, ignore_errors=True)
            
            # Remove downloaded archive
            os.remove(archive_path)

            # Return paths if both executables found
            if len(found_paths) == len(executables):
                return tuple(found_paths)
            
            return None, None

        except Exception as e:
            logging.error(f"Extraction/copy error: {e}")
            return None, None

    def download(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Main download procedure
        Returns paths of ffmpeg and ffprobe
        """
        # First, check if binaries already exist in base directory
        existing_ffmpeg, existing_ffprobe, existing_ffplay = self._check_existing_binaries()
        if existing_ffmpeg and existing_ffprobe:
            return existing_ffmpeg, existing_ffprobe

        # Get latest version
        version = self._get_latest_version()
        if not version:
            logging.error("Cannot proceed: version not found")
            return None, None

        # Prepare configurations
        config = FFMPEG_CONFIGURATION[self.os_name]
        
        # Build download URL
        download_url = config['download_url'].format(
            version=version, 
            arch=self.arch
        )
        
        # Download path
        download_path = os.path.join(
            self.base_dir, 
            f'ffmpeg-{version}{config["file_extension"]}'
        )
        
        # Download
        console.print(
            f"[bold blue]Downloading FFmpeg from:[/] {download_url}", 
        )
        if not self._download_file(download_url, download_path):
            return None, None
        
        # Extract and copy binaries
        ffmpeg_path, ffprobe_path = self._extract_and_copy_binaries(download_path)
        
        if ffmpeg_path and ffprobe_path:
            return ffmpeg_path, ffprobe_path
        
        logging.error("FFmpeg executables not found")
        return None, None


def check_ffmpeg():
    try:
        # First, use 'where' command to check existing binaries on Windows
        if platform.system().lower() == 'windows':
            ffmpeg_path = subprocess.check_output(['where', 'ffmpeg'], text=True).strip().split('\n')[0] if subprocess.call(['where', 'ffmpeg'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0 else None
            ffprobe_path = subprocess.check_output(['where', 'ffprobe'], text=True).strip().split('\n')[0] if subprocess.call(['where', 'ffprobe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0 else None
            
            if ffmpeg_path and ffprobe_path:
                return ffmpeg_path, ffprobe_path
        
        # Fallback to which/shutil method for Unix-like systems
        ffmpeg_path = shutil.which('ffmpeg')
        ffprobe_path = shutil.which('ffprobe')
        
        if ffmpeg_path and ffprobe_path:
            return ffmpeg_path, ffprobe_path
        
        downloader = FFMPEGDownloader()
        return downloader.download()
    
    except Exception as e:
        logging.error(f"Error checking FFmpeg: {e}")
        return None, None
