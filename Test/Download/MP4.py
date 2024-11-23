# 23.06.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(src_path)



# Import
from StreamingCommunity.Src.Util.message import start_message
from StreamingCommunity.Src.Util.logger import Logger
from StreamingCommunity.Src.Lib.Downloader import MP4_downloader


# Test
start_message()
logger = Logger()
print("Return: ", MP4_downloader(
    "",
    ".\Video\undefined.mp4"
))
