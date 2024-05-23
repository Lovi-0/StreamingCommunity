# 16.04.24

import re
import sys
import logging
import threading
import subprocess
from datetime import datetime

from typing import Tuple


# Internal utilities
from Src.Util.console import console
from Src.Util.os import format_size


# Variable
terminate_flag = threading.Event()


def capture_output(process: subprocess.Popen, description: str) -> None:
    """
    Function to capture and print output from a subprocess.

    Args:
        - process (subprocess.Popen): The subprocess whose output is captured.
        - description (str): Description of the command being executed.
    """
    try:

        # Variable to store the length of the longest progress string
        max_length = 0

        for line in iter(process.stdout.readline, b''):
            logging.info(f"FFMPEG: {line}")

            # Check if termination is requested
            if terminate_flag.is_set():
                break

            if line is not None and "size=" in str(line).strip():

                # Parse the output line to extract relevant information
                data = parse_output_line(str(line).strip())

                if 'q' in data:
                    is_end = (float(data.get('q')) == -1.0)

                    if not is_end:
                        byte_size = int(re.findall(r'\d+', data.get('size'))[0]) * 1000
                    else:
                        byte_size = int(re.findall(r'\d+', data.get('Lsize'))[0]) * 1000
                else:
                    byte_size = int(re.findall(r'\d+', data.get('size'))[0]) * 1000

                time_now = datetime.now().strftime('%H:%M:%S')

                # Construct the progress string with formatted output information
                progress_string = f"[blue][{time_now}][purple] FFmpeg [white][{description}[white]]: [white]([green]'speed': [yellow]{data.get('speed')}[white], [green]'size': [yellow]{format_size(byte_size)}[white])"
                max_length = max(max_length, len(progress_string))

                # Print the progress string to the console, overwriting the previous line
                console.print(progress_string.ljust(max_length), end="\r")

    except Exception as e:
        logging.error(f"Error in capture_output: {e}")

    finally:
        terminate_process(process)


def parse_output_line(line: str) -> Tuple[str, str]:
    """
    Function to parse the output line and extract relevant information.

    Args:
        - line (str): The output line to parse.

    Returns:
        dict: A dictionary containing parsed information.
        Ex. {'speed': '60.0x'}
    """
    data = {}

    # Split the line by whitespace and extract key-value pairs
    parts = line.replace("  ", "").replace("= ", "=").split()

    for part in parts:
        key_value = part.split('=')

        if len(key_value) == 2:
            key = key_value[0]
            value = key_value[1]
            data[key] = value

    return data


def terminate_process(process):
    """
    Function to terminate a subprocess if it's still running.

    Args:
        - process (subprocess.Popen): The subprocess to terminate.
    """
    if process.poll() is None:  # Check if the process is still running
        process.kill()


def capture_ffmpeg_real_time(ffmpeg_command: list, description: str) -> None:
    """
    Function to capture real-time output from ffmpeg process.

    Args:
        - ffmpeg_command (list): The command to execute ffmpeg.
        - description (str): Description of the command being executed.
    """

    global terminate_flag

    # Clear the terminate_flag before starting a new capture
    terminate_flag.clear()

    # Start the ffmpeg process with subprocess.Popen
    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # Start a thread to capture and print output
    output_thread = threading.Thread(target=capture_output, args=(process,description))
    output_thread.start()

    try:
        # Wait for ffmpeg process to complete
        process.wait()
    except KeyboardInterrupt:
        print("Terminating ffmpeg process...")
    except Exception as e:
        logging.error(f"Error in ffmpeg process: {e}")
    finally:
        terminate_flag.set()  # Signal the output capture thread to terminate
        output_thread.join()  # Wait for the output capture thread to complete

