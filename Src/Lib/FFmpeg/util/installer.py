# 24.01.2023


import logging
import os
import shutil
import subprocess
import urllib.request


# External libraries
from tqdm.rich import tqdm


# Internal utilities
from Src.Util.os import decompress_file
from Src.Util._win32 import set_env_path
from Src.Util.console import console

# Constants
FFMPEG_BUILDS = {
    'release-full': {
        '7z': ('release-full', 'full_build'),
        'zip': (None, 'full_build')
    }
}
INSTALL_DIR = os.path.expanduser("~")

# Variable
show_version = False


def get_version():
    """
    Get the version of FFmpeg installed on the system.

    This function runs the 'ffmpeg -version' command to retrieve version information
    about the installed FFmpeg binary.
    """

    try:
        # Run the FFmpeg command to get version information
        output = subprocess.check_output(['ffmpeg', '-version'], stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Extract version information from the output
        version_lines = [line for line in output.split('\n') if line.startswith('ffmpeg version')]

        if version_lines:

            # Extract version number from the version line
            version = version_lines[0].split(' ')[2]
            console.print(f"[blue]FFmpeg version: [red]{version}")

    except subprocess.CalledProcessError as e:
        # If there's an error executing the FFmpeg command
        print("Error executing FFmpeg command:", e.output.strip())
        raise e

def get_ffmpeg_download_url(build: str = 'release-full', format: str = 'zip') -> str:
    '''
    Construct the URL for downloading FFMPEG build.

    Args:
        build (str): The type of FFMPEG build.
        format (str): The format of the build (e.g., zip, 7z).

    Returns:
        str: The URL for downloading the FFMPEG build.
    '''
    for ffbuild_name, formats in FFMPEG_BUILDS.items():
        for ffbuild_format, names in formats.items():
            if not (format is None or format == ffbuild_format):
                continue

            if names[0]:
                return f'https://gyan.dev/ffmpeg/builds/ffmpeg-{names[0]}.{ffbuild_format}'
            if names[1]:
                github_version = urllib.request.urlopen(
                    'https://www.gyan.dev/ffmpeg/builds/release-version').read().decode()
                assert github_version, 'failed to retreive latest version from github'
                return (
                    'https://github.com/GyanD/codexffmpeg/releases/download/'
                    f'{github_version}/ffmpeg-{github_version}-{names[1]}.{ffbuild_format}'
                )
            
    raise ValueError(f'{build} as format {format} does not exist')

class FFMPEGDownloader:
    def __init__(self, url: str, destination: str, hash_url: str = None) -> None:
        '''
        Initialize the FFMPEGDownloader object.

        Args:
            url (str): The URL to download the file from.
            destination (str): The path where the downloaded file will be saved.
            hash_url (str): The URL containing the file's expected hash.
        '''
        self.url = url
        self.destination = destination
        self.expected_hash = urllib.request.urlopen(hash_url).read().decode() if hash_url is not None else None
        with urllib.request.urlopen(self.url) as data:
            self.file_size = data.length

    def download(self) -> None:
        '''
        Download the file from the provided URL.
        '''
        try:
            with urllib.request.urlopen(self.url) as response, open(self.destination, 'wb') as out_file:
                with tqdm(total=self.file_size, unit='B', unit_scale=True, unit_divisor=1024, desc='[yellow]Downloading') as pbar:
                    while True:
                        data = response.read(4096)
                        if not data:
                            break
                        out_file.write(data)
                        pbar.update(len(data))
        except Exception as e:
            logging.error(f"Error downloading file: {e}")
            raise

def move_ffmpeg_exe_to_top_level(install_dir: str) -> None:
    '''
    Move the FFMPEG executable to the top-level directory.

    Args:
        install_dir (str): The directory to search for the executable.
    '''
    try:
        for root, _, files in os.walk(install_dir):
            for file in files:
                if file == 'ffmpeg.exe':
                    base_path = os.path.abspath(os.path.join(root, '..'))
                    to_remove = os.listdir(install_dir)

                    # Move ffmpeg.exe to the top level
                    for item in os.listdir(base_path):
                        shutil.move(os.path.join(base_path, item), install_dir)

                    # Remove other files from the top level
                    for item in to_remove:
                        item = os.path.join(install_dir, item)
                        if os.path.isdir(item):
                            shutil.rmtree(item)
                        else:
                            os.remove(item)
                    break
    except Exception as e:
        logging.error(f"Error moving ffmpeg executable: {e}")
        raise

def add_install_dir_to_environment_path(install_dir: str) -> None:
    """
    Add the install directory to the environment PATH variable.

    Args:
        install_dir (str): The directory to be added to the environment PATH variable.
    """

    install_dir = os.path.abspath(os.path.join(install_dir, 'bin'))
    set_env_path(install_dir)

def download_ffmpeg():
    """
    Main function to donwload ffmpeg and add to win path
    """
        
    # Get FFMPEG download URL
    ffmpeg_url = get_ffmpeg_download_url()

    # Generate install directory path
    install_dir = os.path.join(INSTALL_DIR, 'FFMPEG')

    console.print(f"[cyan]Making install directory: [red]{install_dir!r}")
    logging.info(f'Making install directory {install_dir!r}')
    os.makedirs(install_dir, exist_ok=True)

    # Download FFMPEG
    console.print(f'[cyan]Downloading: [red]{ffmpeg_url!r} [cyan]to [red]{os.path.join(install_dir, os.path.basename(ffmpeg_url))!r}')
    logging.info(f'Downloading {ffmpeg_url!r} to {os.path.join(install_dir, os.path.basename(ffmpeg_url))!r}')
    downloader = FFMPEGDownloader(ffmpeg_url, os.path.join(install_dir, os.path.basename(ffmpeg_url)))
    downloader.download()

    # Decompress downloaded file
    console.print(f'[cyan]Decompressing downloaded file to: [red]{install_dir!r}')
    logging.info(f'Decompressing downloaded file to {install_dir!r}')
    decompress_file(os.path.join(install_dir, os.path.basename(ffmpeg_url)), install_dir)

    # Move ffmpeg executable to top level
    console.print(f'[cyan]Moving ffmpeg executable to top level of [red]{install_dir!r}')
    logging.info(f'Moving ffmpeg executable to top level of {install_dir!r}')
    move_ffmpeg_exe_to_top_level(install_dir)

    # Add install directory to environment PATH variable
    console.print(f'[cyan]Adding [red]{install_dir} [cyan]to environment PATH variable')
    logging.info(f'Adding {install_dir} to environment PATH variable')
    add_install_dir_to_environment_path(install_dir)

def check_ffmpeg() -> bool:
    """
    Check if FFmpeg is installed and available on the system PATH.

    This function checks if FFmpeg is installed and available on the system PATH.
    If FFmpeg is found, it prints its version. If not found, it attempts to download
    FFmpeg and add it to the system PATH.

    Returns:
        bool: If ffmpeg is present or not
    """

    console.print("[green]Checking FFmpeg...")

    try:

        # Try running the FFmpeg command to check if it exists
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        console.print("[blue]FFmpeg is installed. \n")

        # Get and print FFmpeg version
        if show_version:
            get_version()

        return True

    except:

        try:
            # If FFmpeg is not found, attempt to download and add it to the PATH
            console.print("[cyan]FFmpeg is not found in the PATH. Downloading and adding to the PATH...[/cyan]")

            # Download FFmpeg and add it to the PATH
            download_ffmpeg()
            raise

        except Exception as e:

            # If unable to download or add FFmpeg to the PATH
            console.print("[red]Unable to download or add FFmpeg to the PATH.[/red]")
            console.print(f"Error: {e}")

    return False