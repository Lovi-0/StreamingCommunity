# 03.07.24

import os


# Internal utilities
from StreamingCommunity.Util.console import console
from StreamingCommunity.Util.os import os_manager
from StreamingCommunity.Util.message import start_message
from StreamingCommunity.Lib.Downloader import HLS_Downloader


# Logic class
from StreamingCommunity.Api.Template.Class.SearchType import MediaItem


# Player
from StreamingCommunity.Api.Player.maxstream import VideoSource


# Config
from .costant import MOVIE_FOLDER


def download_film(select_title: MediaItem) -> str:
    """
    Downloads a film using the provided obj.

    Parameters:
        - select_title (MediaItem): The media item to be downloaded. This should be an instance of the MediaItem class, containing attributes like `name` and `url`.

    Return:
        - str: output path
    """
    start_message()
    console.print(f"[yellow]Download:  [red]{select_title.name} \n")
    console.print(f"[cyan]You can safely stop the download with [bold]Ctrl+c[bold] [cyan] \n")

    # Setup api manger
    print(select_title.url)
    video_source = VideoSource(select_title.url)

    # Define output path
    title_name = os_manager.get_sanitize_file(select_title.name) +".mp4"
    mp4_path = os.path.join(MOVIE_FOLDER, title_name.replace(".mp4", ""))

    # Get m3u8 master playlist
    master_playlist = video_source.get_playlist()

    # Download the film using the m3u8 playlist, and output filename
    r_proc = HLS_Downloader(
        m3u8_playlist=master_playlist, 
        output_filename=os.path.join(mp4_path, title_name)
    ).start()

    if "error" in r_proc.keys():
        try:
            os.remove(r_proc['path'])
        except:
            pass

    return r_proc['path']