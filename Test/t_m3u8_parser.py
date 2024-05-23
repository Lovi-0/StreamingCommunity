# 14.05.24

# Fix import
import time
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)

def read_file(file_path):
    with open(file_path, "r") as file:
        m3u8_content = file.read()
    return m3u8_content



# Import
from Src.Lib.M3U8.lib_parser import M3U8
from Src.Lib.M3U8 import M3U8_Parser



# Test data
obj_m3u8_parser = M3U8_Parser()
base_path_file = os.path.join('Test', 'data', 'm3u8')
index_audio = read_file(os.path.join(base_path_file, "index_audio.m3u8"))
index_subtitle = read_file(os.path.join(base_path_file,"index_subtitle.m3u8"))
index_video = read_file(os.path.join(base_path_file, "index_video.m3u8"))
playlist = read_file(os.path.join(base_path_file, "playlist.m3u8"))


print("AUDIO: ")
print(M3U8(index_audio).data)
print()

print("SUBTITLE: ")
print(M3U8(index_subtitle).data)
print()

print("INDEX: ")
print(M3U8(index_video).data)
print()

print("PLAYLIST: ")
print(M3U8(playlist).data)
