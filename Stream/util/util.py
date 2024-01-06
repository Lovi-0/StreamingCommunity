# 4.01.2023

# Import
import ffmpeg, subprocess

def convert_utf8_name(name):
    return str(name).encode('utf-8').decode('latin-1')

def there_is_audio(ts_file_path):
    probe = ffmpeg.probe(ts_file_path)
    return any(stream['codec_type'] == 'audio' for stream in probe['streams'])


def merge_ts_files(video_path, audio_path, output_path):
    
    """command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c', 'copy',
            '-map', '0',
            '-map', '1',
            '-y', output_path
        ]

    subprocess.run(command)"""

    input_video = ffmpeg.input(video_path)
    input_audio = ffmpeg.input(audio_path)

    ffmpeg.output(input_video, input_audio, output_path, format='mpegts', acodec='copy', vcodec='copy', loglevel='quiet').run()