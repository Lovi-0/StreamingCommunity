# 31.01.24

# Class import
from Src.Util.Helper.console import console

# Import
import ffmpeg 

def get_video_duration(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        duration = float(probe['format']['duration'])
        return duration
    except ffmpeg.Error as e:
        print(f"Error: {e.stderr}")
        return None

def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(hours), int(minutes), int(seconds)

def print_duration_table(file_path):
    video_duration = get_video_duration(file_path)

    if video_duration is not None:
        hours, minutes, seconds = format_duration(video_duration)
        console.log(f"[cyan]Info [green]'{file_path}': [purple]{int(hours)}[red]h [purple]{int(minutes)}[red]m [purple]{int(seconds)}[red]s")