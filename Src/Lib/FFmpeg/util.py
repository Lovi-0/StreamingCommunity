# 31.01.24

# Class
from Src.Util.console import console

# Import
import ffmpeg


# Variable


# [ func ]
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
        console.log(
            f"[cyan]Info [green]'{file_path}': [purple]{int(hours)}[red]h [purple]{int(minutes)}[red]m [purple]{int(seconds)}[red]s")


def audio_extractor_m3u8(req):
    m3u8_cont = req.text.split()
    m3u8_cont_arr = []
    for row in m3u8_cont:
        if "audio" in str(row):
            lang = None
            default = False
            for field in row.split(","):
                if "NAME" in field:
                    lang = field.split('"')[-2]
                if "DEFAULT" in field:
                    default_str = field.split('=')[1]
                    default = default_str.strip() == "YES"
            audioobj = {"url": row.split(",")[-1].split('"')[-2], "lang": lang, "default": default}
            if audioobj['lang'] is None:
                continue
            m3u8_cont_arr.append(audioobj)
    return m3u8_cont_arr or None
