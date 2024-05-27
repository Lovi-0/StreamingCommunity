# 31.01.24

import os
import sys
import time
import logging
import shutil
import threading
import subprocess

from typing import List, Dict


# External libraries
try: import ffmpeg # type: ignore
except: pass


# Internal utilities
from Src.Util._jsonConfig import config_manager
from Src.Util.os import check_file_existence
from Src.Util.console import console
from .util import has_audio_stream, need_to_force_to_ts, check_ffmpeg_input
from .capture import capture_ffmpeg_real_time


# Variable
DEBUG_MODE = config_manager.get_bool("DEFAULT", "debug")
DEBUG_FFMPEG = "debug" if DEBUG_MODE else "error"
USE_CODECS = config_manager.get_bool("M3U8_FILTER", "use_codec")
USE_GPU = config_manager.get_bool("M3U8_FILTER", "use_gpu")
FFMPEG_DEFAULT_PRESET = config_manager.get("M3U8_FILTER", "default_preset")
CHECK_OUTPUT_CONVERSION = config_manager.get_bool("M3U8_FILTER", "check_output_conversion")



# --> v 1.0 (deprecated)
def __concatenate_and_save(file_list_path: str, output_filename: str, v_codec: str = None, a_codec: str = None, bandwidth: int = None, prefix: str = "segments", output_directory: str = None):
    """
    Concatenate input files and save the output with specified decoding parameters.

    Args:
        - file_list_path (str): Path to the file list containing the segments.
        - output_filename (str): Output filename for the concatenated video.
        - v_codec (str): Video decoding parameter (optional).
        - a_codec (str): Audio decoding parameter (optional).
        - bandwidth (int): Bitrate for the output video (optional).
        - prefix (str): Prefix to add at the end of output file name (default is "segments").
        - output_directory (str): Directory to save the output file. If not provided, defaults to the current directory.
        - codecs (str): Codecs for video and audio (optional).

    Returns:
        output_file_path (str): Path to the saved output file.
    """

    try:

        # Output arguments
        output_args = {
            'c': 'copy',
            'loglevel': DEBUG_FFMPEG,
        }

        # Set up the output file name by modifying the video file name
        output_file_name = output_filename
        output_file_path = os.path.join(output_directory, output_file_name) if output_directory else output_file_name

        # Concatenate input file list and output
        output = (
            ffmpeg.input(file_list_path, safe=0, f='concat')
            .output(output_file_path, **output_args)
        )

        # Overwrite output file if exists
        output = ffmpeg.overwrite_output(output)

        # Execute the process
        process = output.run()

    except ffmpeg.Error as ffmpeg_error:
        logging.error(f"Error saving MP4: {ffmpeg_error.stderr.decode('utf-8')}")
        return ""

    # Remove the temporary file list and folder and completely remove tmp folder
    os.remove(file_list_path)
    shutil.rmtree("tmp", ignore_errors=True)
    return output_file_path

def __join_audios(video_path: str, audio_tracks: List[Dict[str, str]], prefix: str = "merged") -> str:
    """
    Join video with multiple audio tracks and sync them if there are matching segments.

    Args:
        - video_path (str): Path to the video file.
        - audio_tracks (List[Dict[str, str]]): A list of dictionaries, where each dictionary contains 'audio_path'.
        - prefix (str, optional): Prefix to add at the beginning of the output filename. Defaults to "merged".
    
    Returns:
        out_path (str): Path to the saved output video file.
    """

    try:

        # Check if video_path exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file '{video_path}' not found.")

        # Create input streams for video and audio using ffmpeg's.
        video_stream = ffmpeg.input(video_path)

        # Create a list to store audio streams and map arguments
        audio_streams = []
        map_arguments = []

        # Iterate through audio tracks
        for i, audio_track in enumerate(audio_tracks):
            audio_path = audio_track.get('path', '')

            # Check if audio_path exists
            if audio_path:
                if not os.path.exists(audio_path):
                    logging.warning(f"Audio file '{audio_path}' not found.")
                    continue
                
                audio_stream = ffmpeg.input(audio_path)
                audio_streams.append(audio_stream)
                map_arguments.extend(['-map', f'{i + 1}:a:0'])

        # Set up a process to combine the video and audio streams and create an output file with .mp4 extension.
        output_file_name = f"{prefix}_{os.path.splitext(os.path.basename(video_path))[0]}.mp4"
        out_path = os.path.join(os.path.dirname(video_path), output_file_name)

        # Output arguments
        output_args = {
            'vcodec': 'copy',
            'acodec': 'copy',
            'loglevel': DEBUG_FFMPEG
        }

        # Combine inputs, map audio streams, and set output
        output = (
            ffmpeg.output(
                video_stream,
                *audio_streams,
                out_path,
                **output_args
            )
            .global_args(
                '-map', '0:v:0',
                *map_arguments,
                '-shortest',
                '-strict', 'experimental',
            )
        )

        # Overwrite output file if exists
        output = ffmpeg.overwrite_output(output)

        # Retrieve the command that will be executed
        command = output.compile()
        logging.info(f"Execute command: {command}")

        # Execute the process
        process = output.run()
        logging.info("[M3U8_Downloader] Merge completed successfully.")

        # Return
        return out_path

    except ffmpeg.Error as ffmpeg_error:
        logging.error("[M3U8_Downloader] Ffmpeg error: %s", ffmpeg_error)
        return ""

def __transcode_with_subtitles(video: str, subtitles_list: List[Dict[str, str]], output_file: str, prefix: str = "transcoded") -> str:

    """
    Transcode a video with subtitles.
    
    Args:
        - video (str): Path to the input video file.
        - subtitles_list (list[dict[str, str]]): List of dictionaries containing subtitles information.
        - output_file (str): Path to the output transcoded video file.
        - prefix (str): Prefix to add to the output file name. Default is "transcoded".
    
    Returns:
        str: Path to the transcoded video file.
    """

    try:
        
        # Check if the input video file exists
        if not os.path.exists(video):
            raise FileNotFoundError(f"Video file '{video}' not found.")

        # Get input video from video path
        input_ffmpeg = ffmpeg.input(video)
        input_video = input_ffmpeg['v']
        input_audio = input_ffmpeg['a']

        # List with subtitles path and metadata
        input_subtitles = []
        metadata = {}

        # Iterate through subtitle tracks
        for idx, sub_dict in enumerate(subtitles_list):
            # Get path and name of subtitles
            sub_file = sub_dict.get('path')
            title = sub_dict.get('name')

            # Check if the subtitle file exists
            if not os.path.exists(sub_file):
                raise FileNotFoundError(f"Subtitle file '{sub_file}' not found.")

            # Append ffmpeg input to list
            input_ffmpeg_sub = ffmpeg.input(sub_file)
            input_subtitles.append(input_ffmpeg_sub['s'])

            # Add metadata for title
            metadata[f'metadata:s:s:{idx}'] = f"title={title}"

        # Check if the input video has an audio stream
        logging.info(f"There is audio: {has_audio_stream(video)}")

        # Set up the output file name by adding the prefix
        output_filename = f"{prefix}_{os.path.splitext(os.path.basename(video))[0]}.mkv"
        output_file = os.path.join(os.path.dirname(output_file), output_filename)

        # Configure ffmpeg output
        output = ffmpeg.output(
            input_video,
            *(input_audio,) if has_audio_stream(video) else (),     # If there is no audio stream
            *input_subtitles,
            output_file,
            vcodec='copy',
            acodec='copy' if has_audio_stream(video) else (),       # If there is no audio stream
            **metadata,
            loglevel=DEBUG_FFMPEG
        )

        # Overwrite output file if exists
        output = ffmpeg.overwrite_output(output)

        # Retrieve the command that will be executed
        command = output.compile()
        logging.info(f"Execute command: {command}")

        # Run ffmpeg command
        ffmpeg.run(output, overwrite_output=True)

        # Rename video from mkv -> mp4
        output_filename_mp4 = output_file.replace("mkv", "mp4")
        os.rename(output_file, output_filename_mp4)

        return output_filename_mp4

    except ffmpeg.Error as ffmpeg_error:
        print(f"Error: {ffmpeg_error}")
        return ""



# --> v 1.1 (new)
def join_video(video_path: str, out_path: str, vcodec: str = None, acodec: str = None, bitrate: str = None):
    
    """
    Joins single ts video file to mp4
    
    Args:
        - video_path (str): The path to the video file.
        - out_path (str): The path to save the output file.
        - vcodec (str): The video codec to use. Defaults to 'copy'.
        - acodec (str): The audio codec to use. Defaults to 'aac'.
        - bitrate (str): The bitrate for the audio stream. Defaults to '192k'.
        - force_ts (bool): Force video path to be mpegts as input.
    """

    if not check_file_existence(video_path):
        logging.error("Missing input video for ffmpeg conversion.")
        sys.exit(0)

    # Start command
    ffmpeg_cmd = ['ffmpeg']

    # Enabled the use of gpu
    ffmpeg_cmd.extend(['-hwaccel', 'cuda', '-hwaccel_output_format', 'cuda'])

    # Add mpegts to force to detect input file as ts file
    if need_to_force_to_ts(video_path):
        console.log("[red]Force input file to 'mpegts'.")
        ffmpeg_cmd.extend(['-f', 'mpegts'])
        vcodec = "libx264"

    # Insert input video path
    ffmpeg_cmd.extend(['-i', video_path])

    # Add output args
    if USE_CODECS:
        if vcodec: ffmpeg_cmd.extend(['-c:v', vcodec])
        if acodec: ffmpeg_cmd.extend(['-c:a', acodec])
        if bitrate: ffmpeg_cmd.extend(['-b:a', str(bitrate)])
    else:
        ffmpeg_cmd.extend(['-c', 'copy'])

    # Ultrafast preset always or fast for gpu
    if not USE_GPU:
        ffmpeg_cmd.extend(['-preset', FFMPEG_DEFAULT_PRESET])
    else:
        ffmpeg_cmd.extend(['-preset', 'fast'])

    # Overwrite
    ffmpeg_cmd += [out_path, "-y"]
    logging.info(f"FFmpeg command: {ffmpeg_cmd}")

    # Run join
    if DEBUG_MODE:
        subprocess.run(ffmpeg_cmd, check=True)
    else:
        capture_ffmpeg_real_time(ffmpeg_cmd, "[cyan]Join video")
        print()

    # Check file
    if CHECK_OUTPUT_CONVERSION:
        console.log("[red]Check output ffmpeg")
        time.sleep(0.5)
        check_ffmpeg_input(out_path)


def join_audios(video_path: str, audio_tracks: List[Dict[str, str]], out_path: str, vcodec: str = 'copy', acodec: str = 'aac', bitrate: str = '192k'):
    """
    Joins audio tracks with a video file using FFmpeg.
    
    Args:
        - video_path (str): The path to the video file.
        - audio_tracks (list[dict[str, str]]): A list of dictionaries containing information about audio tracks.
            Each dictionary should contain the 'path' key with the path to the audio file.
        - out_path (str): The path to save the output file.
        - vcodec (str): The video codec to use. Defaults to 'copy'.
        - acodec (str): The audio codec to use. Defaults to 'aac'.
        - bitrate (str): The bitrate for the audio stream. Defaults to '192k'.
        - preset (str): The preset for encoding. Defaults to 'ultrafast'.
    """

    if not check_file_existence(video_path):
        logging.error("Missing input video for ffmpeg conversion.")
        sys.exit(0)

    # Start command
    ffmpeg_cmd = ['ffmpeg', '-i', video_path]

    # Add audio track
    for i, audio_track in enumerate(audio_tracks):
        ffmpeg_cmd.extend(['-i',  audio_track.get('path')])

        if not check_file_existence(audio_track.get('path')):
            sys.exit(0)

    # Add output args
    if USE_CODECS:
        ffmpeg_cmd.extend(['-c:v', vcodec, '-c:a', acodec, '-b:a', str(bitrate), '-preset', FFMPEG_DEFAULT_PRESET])
    else:
        ffmpeg_cmd.extend(['-c', 'copy'])

    # Overwrite
    ffmpeg_cmd += [out_path, "-y"]
    logging.info(f"FFmpeg command: {ffmpeg_cmd}")

    # Run join
    if DEBUG_MODE:
        subprocess.run(ffmpeg_cmd, check=True)
    else:
        capture_ffmpeg_real_time(ffmpeg_cmd, "[cyan]Join audio")
        print()


    # Check file
    if CHECK_OUTPUT_CONVERSION:
        console.log("[red]Check output ffmpeg")
        time.sleep(0.5)
        check_ffmpeg_input(out_path)


def join_subtitle(video_path: str, subtitles_list: List[Dict[str, str]], out_path: str):
    """
    Joins subtitles with a video file using FFmpeg.
    
    Args:
        - video (str): The path to the video file.
        - subtitles_list (list[dict[str, str]]): A list of dictionaries containing information about subtitles.
            Each dictionary should contain the 'path' key with the path to the subtitle file and the 'name' key with the name of the subtitle.
        - out_path (str): The path to save the output file.
    """

    if not check_file_existence(video_path):
        logging.error("Missing input video for ffmpeg conversion.")
        sys.exit(0)


    # Start command
    added_subtitle_names = set()    # Remove subtitle with same name
    ffmpeg_cmd = ["ffmpeg", "-i", video_path]

    # Add subtitle with language
    for idx, subtitle in enumerate(subtitles_list):

        if subtitle['name'] in added_subtitle_names:
            continue
    
        added_subtitle_names.add(subtitle['name'])

        ffmpeg_cmd += ["-i", subtitle['path']]
        ffmpeg_cmd += ["-map", "0:v", "-map", "0:a", "-map", f"{idx + 1}:s"]
        ffmpeg_cmd += ["-metadata:s:s:{}".format(idx), "title={}".format(subtitle['name'])]

        if not check_file_existence(subtitle['path']):
            sys.exit(0)

    # Add output args
    if USE_CODECS:
        ffmpeg_cmd.extend(['-c:v', 'copy', '-c:a', 'copy', '-c:s', 'mov_text'])
    else:
        ffmpeg_cmd.extend(['-c', 'copy', '-c:s', 'mov_text'])

    # Overwrite
    ffmpeg_cmd += [out_path, "-y"]
    logging.info(f"FFmpeg command: {ffmpeg_cmd}")

    # Run join
    if DEBUG_MODE:
        subprocess.run(ffmpeg_cmd, check=True)
    else:
        capture_ffmpeg_real_time(ffmpeg_cmd, "[cyan]Join subtitle")
        print()

    # Check file
    if CHECK_OUTPUT_CONVERSION:
        console.log("[red]Check output ffmpeg")
        time.sleep(0.5)
        check_ffmpeg_input(out_path)
