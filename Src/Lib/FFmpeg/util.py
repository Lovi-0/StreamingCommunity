# 16.04.24

import os
import sys
import json
import subprocess
import logging

from typing import Tuple


# Internal utilities
from Src.Util.console import console


def has_audio_stream(video_path: str) -> bool:
    """
    Check if the input video has an audio stream.

    Args:
        - video_path (str): Path to the input video file.

    Returns:
        has_audio (bool): True if the input video has an audio stream, False otherwise.
    """
    try:
        ffprobe_cmd = ['ffprobe', '-v', 'error', '-print_format', 'json', '-select_streams', 'a', '-show_streams', video_path]
        logging.info(f"FFmpeg command: {ffprobe_cmd}")

        with subprocess.Popen(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            stdout, stderr = proc.communicate()
            if stderr:
                logging.error(f"Error: {stderr}")
            else:
                probe_result = json.loads(stdout)
                return bool(probe_result.get('streams', []))
            
    except Exception as e:
        logging.error(f"Error: {e}")
        return False


def get_video_duration(file_path: str) -> float:
    """
    Get the duration of a video file.

    Args:
        - file_path (str): The path to the video file.

    Returns:
        (float): The duration of the video in seconds if successful, 
        None if there's an error.
    """

    try:
        ffprobe_cmd = ['ffprobe', '-v', 'error', '-show_format', '-print_format', 'json', file_path]
        logging.info(f"FFmpeg command: {ffprobe_cmd}")

        # Use a with statement to ensure the subprocess is cleaned up properly
        with subprocess.Popen(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            stdout, stderr = proc.communicate()
            
            if proc.returncode != 0:
                logging.error(f"Error: {stderr}")
                return None
            
            # Parse JSON output
            probe_result = json.loads(stdout)

            # Extract duration from the video information
            return float(probe_result['format']['duration'])
    
    except Exception as e:
        logging.error(f"Error: {e}")
        return None


def format_duration(seconds: float) -> Tuple[int, int, int]:
    """
    Format duration in seconds into hours, minutes, and seconds.

    Args:
        - seconds (float): Duration in seconds.

    Returns:
        list[int, int, int]: List containing hours, minutes, and seconds.
    """

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return int(hours), int(minutes), int(seconds)


def print_duration_table(file_path: str) -> None:
    """
    Print duration of a video file in hours, minutes, and seconds.

    Args:
        - file_path (str): The path to the video file.
    """

    video_duration = get_video_duration(file_path)

    if video_duration is not None:
        hours, minutes, seconds = format_duration(video_duration)
        console.log(f"[cyan]Duration for [white]([green]{os.path.basename(file_path)}[white]): [yellow]{int(hours)}[red]h [yellow]{int(minutes)}[red]m [yellow]{int(seconds)}[red]s")
