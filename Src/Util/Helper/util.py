# 4.01.2023

# Import
import ffmpeg, subprocess, re

def convert_utf8_name(name):
    return str(name).encode('utf-8').decode('latin-1')

def there_is_audio(ts_file_path):
    probe = ffmpeg.probe(ts_file_path)
    return any(stream['codec_type'] == 'audio' for stream in probe['streams'])

def merge_ts_files(video_path, audio_path, output_path):
    input_video = ffmpeg.input(video_path)
    input_audio = ffmpeg.input(audio_path)

    ffmpeg_command = ffmpeg.output(input_video, input_audio, output_path, format='mpegts', acodec='copy', vcodec='copy', loglevel='quiet').compile()

    try:
        subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        #print(f"Failed convert: {video_path} \ {audio_path} to {output_path}")
        return False