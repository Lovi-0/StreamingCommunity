# 4.01.2023

# Import
from moviepy.editor import VideoFileClip

def convert_utf8_name(name):
    return str(name).encode('utf-8').decode('latin-1')

def check_audio_presence(file_path):
    try:
        video_clip = VideoFileClip(file_path)
        audio = video_clip.audio
        return audio is not None
    except Exception as e:
        print(f"Si è verificato un errore: {str(e)}")