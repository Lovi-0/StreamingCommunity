# 4.01.2023

# Class import
from Src.Util.Helper.console import console, config_logger

# General import
import ffmpeg, subprocess, logging

def there_is_audio(ts_file_path):
    probe = ffmpeg.probe(ts_file_path)
    return any(stream['codec_type'] == 'audio' for stream in probe['streams'])

def merge_ts_files(video_path, audio_path, output_path):
    input_video = ffmpeg.input(video_path)
    input_audio = ffmpeg.input(audio_path)
    logging.debug(f"Merge video ts: {input_video}, with audio ts: {input_audio}, to: {output_path}")

    ffmpeg_command = ffmpeg.output(input_video, input_audio, output_path, format='mpegts', acodec='copy', vcodec='copy', loglevel='quiet').compile()

    try:
        subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE)
        logging.debug(f"Saving: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Can save: {output_path}")
        return False