# 31.01.24

import subprocess
import os
import json
import logging
import shutil


# External libraries
import ffmpeg


# Internal utilities
from Src.Util.console import console
from Src.Util.config import config_manager


# Variable
DEBUG_MODE = config_manager.get_bool("DEFAULT", "debug")
DEBUG_FFMPEG = "debug" if DEBUG_MODE else "error"
USE_CODECS = config_manager.get_bool("M3U8", "use_codecs")



"""
DOC:

The `'c': 'copy'` option in the `output_args` dictionary indicates that ffmpeg should perform stream copying for both the audio and video streams. 
Stream copying means that the audio and video streams are copied directly from the input file(s) to the output file without any re-encoding. 
This process preserves the original quality of the streams and is much faster than re-encoding.

When using `'c': 'copy'`, ffmpeg simply copies the bitstream from the input file(s) to the output file without decoding or altering it. 
This is useful when you want to quickly concatenate or merge multimedia files without any loss in quality or additional processing time. 
It's particularly efficient when the input and output formats are compatible, and you don't need to make any modifications to the streams.
"""



def has_audio_stream(video_path: str) -> bool:
    """
    Check if the input video has an audio stream.

    Parameters:
    - video_path (str): Path to the input video file.

    Returns:
    - has_audio (bool): True if the input video has an audio stream, False otherwise.
    """
    
    try:

        ffprobe_cmd = ['ffprobe', '-v', 'error', '-print_format', 'json', '-select_streams', 'a', '-show_streams', video_path]
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)

        # Parse JSON output
        probe_result = json.loads(result.stdout)

        # Check if there are audio streams
        return bool(probe_result.get('streams', []))
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: {e.stderr}")
        return None


def get_video_duration(file_path: str) -> (float):
    """
    Get the duration of a video file.

    Args:
        file_path (str): The path to the video file.

    Returns:
        (float): The duration of the video in seconds if successful, 
        None if there's an error.
    """

    try:

        ffprobe_cmd = ['ffprobe', '-v', 'error', '-show_format', '-print_format', 'json', file_path]
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)

        # Parse JSON output
        probe_result = json.loads(result.stdout)

        # Extract duration from the video information
        return float(probe_result['format']['duration'])
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: {e.stderr}")
        return None


def format_duration(seconds: float) -> list[int, int, int]:
    """
    Format duration in seconds into hours, minutes, and seconds.

    Args:
        seconds (float): Duration in seconds.

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
        file_path (str): The path to the video file.
    """

    video_duration = get_video_duration(file_path)

    if video_duration is not None:

        # Format duration into hours, minutes, and seconds
        hours, minutes, seconds = format_duration(video_duration)

        # Print the formatted duration
        console.log(f"[cyan]Info [green]'{file_path}': [purple]{int(hours)}[red]h [purple]{int(minutes)}[red]m [purple]{int(seconds)}[red]s")


def add_subtitle(input_video_path: str, input_subtitle_path: str, output_video_path: str, subtitle_language: str = 'ita', prefix: str = "single_sub") -> str:
    """
    Convert a video with a single subtitle.

    Args:
        input_video_path (str): Path to the input video file.
        input_subtitle_path (str): Path to the input subtitle file.
        output_video_path (str): Path to save the output video file.
        subtitle_language (str, optional): Language of the subtitle. Defaults to 'ita'.
        prefix (str, optional): Prefix to add at the beginning of the output filename. Defaults to "subtitled".

    Returns:
        output_video_path (str): Path to the saved output video file.
    """

    # Check if input_video_path and input_subtitle_path exist
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video file '{input_video_path}' not found.")
    
    if not os.path.exists(input_subtitle_path):
        raise FileNotFoundError(f"Input subtitle file '{input_subtitle_path}' not found.")
    
    # Set up the output file name by modifying the video file name
    output_filename = os.path.splitext(os.path.basename(input_video_path))[0]
    output_file_name = f"{prefix}_{output_filename}.mp4"
    output_video_path = os.path.join(os.path.dirname(output_video_path), output_file_name)

    # Input settings
    input_video = ffmpeg.input(input_video_path)
    input_subtitle = ffmpeg.input(input_subtitle_path)
    
    # Output settings
    output_args = {
        'c:s': 'mov_text',
        'c:v': 'copy',
        'c:a': 'copy',
        'metadata:s:s:0': 'language=' + subtitle_language,
    }
    
    # Combine inputs, map subtitle stream, and output
    ffmpeg.output(
        input_video, 
        input_subtitle, 
        output_video_path, 
        **output_args
    ).global_args(
        '-map', '0:v', 
        '-map', '0:a', 
        '-map', '1:s'
    ).run()

    # Return
    return output_video_path


def concatenate_and_save(file_list_path: str, output_filename: str, v_codec: str = None, a_codec: str = None, bandwidth: int = None, prefix: str = "segments", output_directory: str = None) -> str:
    """
    Concatenate input files and save the output with specified decoding parameters.

    Parameters:
    - file_list_path (str): Path to the file list containing the segments.
    - output_filename (str): Output filename for the concatenated video.
    - v_codec (str): Video decoding parameter (optional).
    - a_codec (str): Audio decoding parameter (optional).
    - bandwidth (int): Bitrate for the output video (optional).
    - prefix (str): Prefix to add at the end of output file name (default is "segments").
    - output_directory (str): Directory to save the output file. If not provided, defaults to the current directory.
    - codecs (str): Codecs for video and audio (optional).

    Returns:
    - output_file_path (str): Path to the saved output file.
    """

    try:
        # Input and output arguments
        input_args = {
            'format': 'concat', 
            'safe': 0
        }

        output_args = {
            #'preset': 'ultrafast',
            'c': 'copy',
            'loglevel': DEBUG_FFMPEG,
            'y': None,
        }

        # Add BANDWIDTH and CODECS if provided
        if bandwidth is not None:
            output_args['b:v'] = str(bandwidth)
        if USE_CODECS:
            if v_codec is not None:
                output_args['vcodec'] = v_codec
            if a_codec is not None:
                output_args['acodec'] = a_codec

        # Set up the output file name by modifying the video file name
        output_file_name = os.path.splitext(output_filename)[0] + f"_{prefix}.mp4"

        # Determine output directory
        if output_directory:
            output_file_path = os.path.join(output_directory, output_file_name)
        else:
            output_file_path = output_file_name

        # Concatenate input files and output
        output = (
            ffmpeg.input(
                file_list_path, 
                **input_args
            )
            .output(
                output_file_path, 
                **output_args
            )
        )

        # Overwrite output file if exists
        output = ffmpeg.overwrite_output(output)

        # Retrieve the command that will be executed
        command = output.compile()
        logging.info(f"Execute command: {command}")

        # Execute the process
        process = output.run()

    except ffmpeg.Error as ffmpeg_error:

        logging.error(f"Error saving MP4: {ffmpeg_error.stdout}")
        return ""

    # Remove the temporary file list and folder and completely remove tmp folder
    logging.info("Cleanup...")
    os.remove(file_list_path)
    shutil.rmtree("tmp", ignore_errors=True)

    # Return
    return output_file_path


def join_audios(video_path: str, audio_tracks: list[dict[str, str]], prefix: str = "merged") -> str:
    """
    Join video with multiple audio tracks and sync them if there are matching segments.

    Parameters:
    - video_path (str): Path to the video file.
    - audio_tracks (List[Dict[str, str]]): A list of dictionaries, where each dictionary contains 'audio_path'.
    - prefix (str, optional): Prefix to add at the beginning of the output filename. Defaults to "merged".
    
    Returns:
    - out_path (str): Path to the saved output video file.
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


def transcode_with_subtitles(video: str, subtitles_list: list[dict[str, str]], output_file: str, prefix: str = "transcoded") -> str:

    """
    Transcode a video with subtitles.
    
    Args:
    - video (str): Path to the input video file.
    - subtitles_list (list[dict[str, str]]): List of dictionaries containing subtitles information.
    - output_file (str): Path to the output transcoded video file.
    - prefix (str): Prefix to add to the output file name. Default is "transcoded".
    
    Returns:
    - str: Path to the transcoded video file.
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
