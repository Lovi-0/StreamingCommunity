# 23.06.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(src_path)



# Import
from StreamingCommunity.Util.message import start_message
from StreamingCommunity.Util.logger import Logger
from StreamingCommunity.Lib.Downloader import TOR_downloader


# Test
start_message()
logger = Logger()
manager = TOR_downloader()

magnet_link = """magnet:?xt=urn:btih:d1257567d7a76d2e40734f561fd175769285ed33&dn=Alien.Romulus.2024.1080p.BluRay.x264-FHC.mkv&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Ftorrentclub.space%3A6969%2Fannounce&tr=http%3A%2F%2Ftracker.bt4g.com%3A2095%2Fannounce&tr=https%3A%2F%2Ftr.burnabyhighstar.com%3A443%2Fannoun
ce&tr=udp%3A%2F%2Ftracker.monitorit4.me%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.0x.tf%3A6969%2Fannounce&tr=http%3A%2F%2Fbt.okmp3.ru%3A2710%2Fannounce&tr=https%3A%2F%2Ftr.doogh.club%3A443%2Fannounce&tr=https%3A%2F%2Ft.btcland.xyz%3A443%2Fannounce&tr=https%3A%2F%2Ftr.fuckbitcoin.xyz%3A443%2Fannounce&tr=http%3A%2F%2Ftrack
er.files.fm%3A6969%2Fannounce"""
manager.add_magnet_link(magnet_link)
manager.start_download()
manager.move_downloaded_files(".")
