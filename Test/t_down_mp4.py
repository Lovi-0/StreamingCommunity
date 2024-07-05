# 23.06.24

# Fix import
import time
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)



# Import
from Src.Lib.Downloader import MP4_downloader



# Test
MP4_downloader(
    "",
    "EP_2.mp4",
)
