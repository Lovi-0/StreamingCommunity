# 23.06.24

# Fix import
import time
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)



# Import
from Src.Lib.Downloader import HLS_Downloader


# Test
HLS_Downloader(
    output_filename=r".\EP_1.mp4",
    m3u8_playlist=""
).start()