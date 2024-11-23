# 23.06.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(src_path)



# Import
from Src.Util.message import start_message
from Src.Util.logger import Logger
from Src.Lib.Downloader import TOR_downloader


# Test
start_message()
logger = Logger()
manager = TOR_downloader()

magnet_link = "magnet:?x"
manager.add_magnet_link(magnet_link)
manager.start_download()
manager.move_downloaded_files()
