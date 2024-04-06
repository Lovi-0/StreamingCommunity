# 24.01.2023

import subprocess
import os
import requests
import zipfile
import sys
import ctypes


# Internal utilities
from Src.Util.console import console


def isAdmin() -> (bool):
    """ 
    Check if the current user has administrative privileges.

    Returns:
        bool: True if the user is an administrator, False otherwise.
    """

    try:
        is_admin = (os.getuid() == 0)

    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return is_admin


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


def download_ffmpeg():
    """
    Download FFmpeg binary for Windows and add it to the system PATH.

    This function downloads the FFmpeg binary zip file from the specified URL,
    extracts it to a directory named 'ffmpeg', and adds the 'bin' directory of
    FFmpeg to the system PATH so that it can be accessed from the command line.
    """

    # SInizializate start variable
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"
    ffmpeg_dir = "ffmpeg"

    print("[yellow]Downloading FFmpeg...[/yellow]")

    try:
        response = requests.get(ffmpeg_url)

        # Create the directory to extract FFmpeg if it doesn't exist
        os.makedirs(ffmpeg_dir, exist_ok=True)

        # Save the zip file
        zip_file_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(response.content)

        # Extract the zip file
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(ffmpeg_dir)

        # Add the FFmpeg directory to the system PATH
        ffmpeg_bin_dir = os.path.join(os.getcwd(), ffmpeg_dir, "bin")
        os.environ["PATH"] += os.pathsep + ffmpeg_bin_dir

        # Remove the downloaded zip file
        os.remove(zip_file_path)

    except requests.RequestException as e:
        # If there's an issue with downloading FFmpeg
        print(f"Failed to download FFmpeg: {e}")
        raise e

    except zipfile.BadZipFile as e:
        # If the downloaded file is not a valid zip file
        print(f"Failed to extract FFmpeg zip file: {e}")
        raise e


def check_ffmpeg():
    """
    Check if FFmpeg is installed and available on the system PATH.

    This function checks if FFmpeg is installed and available on the system PATH.
    If FFmpeg is found, it prints its version. If not found, it attempts to download
    FFmpeg and add it to the system PATH.
    """

    console.print("[green]Checking FFmpeg...")

    try:
        # Try running the FFmpeg command to check if it exists
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        console.print("[blue]FFmpeg is installed. \n")

        # Get and print FFmpeg version
        #get_version()

    except subprocess.CalledProcessError:
        try:
            # If FFmpeg is not found, attempt to download and add it to the PATH
            console.print("[cyan]FFmpeg is not found in the PATH. Downloading and adding to the PATH...[/cyan]")

            # Check if user has admin privileges
            if not isAdmin():
                console.log("[red]You need to be admin to proceed!")
                sys.exit(0)  

            # Download FFmpeg and add it to the PATH
            download_ffmpeg()
            sys.exit(0)

        except Exception as e:

            # If unable to download or add FFmpeg to the PATH
            console.print("[red]Unable to download or add FFmpeg to the PATH.[/red]")
            console.print(f"Error: {e}")
            sys.exit(0)
