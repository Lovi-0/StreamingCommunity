# 23.06.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(src_path)



# Import
from StreamingCommunity.Util.message import start_message
from StreamingCommunity.Util.os import os_summary
os_summary.get_system_summary()
from StreamingCommunity.Util.logger import Logger
from StreamingCommunity.Lib.Downloader import HLS_Downloader


# Test
start_message()
logger = Logger()
print("Return: ", HLS_Downloader(
    output_path="test.mp4",
    m3u8_url="https://acdn.ak-stream-videoplatform.sky.it/hls/2024/11/21/968275/master.m3u8"
).start())