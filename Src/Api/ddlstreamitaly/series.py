# 13.06.24

import os
import sys
import logging
from urllib.parse import urlparse


# Internal utilities
from Src.Util.console import console
from Src.Util.message import start_message
from Src.Util.os import create_folder, can_create_file
from Src.Util.table import TVShowManager
from Src.Lib.Downloader import MP4_downloader
from ..Template import manage_selection, map_episode_title


# Logic class
from .Core.Class.SearchType import MediaItem
from .Core.Class.ScrapeSerie import GetSerieInfo
from .Core.Player.ddl import VideoSource


# Variable
from .costant import ROOT_PATH, SITE_NAME, SERIES_FOLDER
table_show_manager = TVShowManager()
video_source = VideoSource()



def donwload_video(scape_info_serie: GetSerieInfo, index_episode_selected: int) -> None:
    """
    Download a single episode video.

    Args:
        - tv_name (str): Name of the TV series.
        - index_episode_selected (int): Index of the selected episode.
    """

    start_message()

    # Get info about episode
    obj_episode = scape_info_serie.list_episodes[index_episode_selected - 1]
    console.print(f"[yellow]Download: [red]{obj_episode.get('name')}")
    print()

    # Define filename and path for the downloaded video
    mp4_name = f"{map_episode_title(scape_info_serie.tv_name, None, index_episode_selected, obj_episode.get('name'))}.mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, SERIES_FOLDER, scape_info_serie.tv_name)

    # Check if can create file output
    create_folder(mp4_path)                                                                    
    if not can_create_file(mp4_name):  
        logging.error("Invalid mp4 name.")
        sys.exit(0)

    # Setup video source
    video_source.setup(obj_episode.get('url'))

    # Get m3u8 master playlist
    master_playlist = video_source.get_playlist()
    
    # Parse start page url
    start_message()
    parsed_url = urlparse(obj_episode.get('url'))
    path_parts = parsed_url.path.split('/')

    MP4_downloader(
        url = master_playlist, 
        path = os.path.join(mp4_path, mp4_name),
        referer = f"{parsed_url.scheme}://{parsed_url.netloc}/",
    )


def download_thread(dict_serie: MediaItem):
    """Download all episode of a thread"""

    # Start message and set up video source
    start_message()

    # Init class
    scape_info_serie = GetSerieInfo(dict_serie)

    # Collect information about thread
    list_dict_episode = scape_info_serie.get_episode_number()
    episodes_count = len(list_dict_episode)

    # Display episodes list and manage user selection
    last_command = display_episodes_list(list_dict_episode)
    list_episode_select = manage_selection(last_command, episodes_count)

    # Download selected episodes
    if len(list_episode_select) == 1 and last_command != "*":
        donwload_video(scape_info_serie, list_episode_select[0])

    # Download all other episodes selecter
    else:
        for i_episode in list_episode_select:
            donwload_video(scape_info_serie, i_episode)


def display_episodes_list(obj_episode_manager) -> str:
    """
    Display episodes list and handle user input.

    Returns:
        last_command (str): Last command entered by the user.
    """

    # Set up table for displaying episodes
    table_show_manager.set_slice_end(10)

    # Add columns to the table
    column_info = {
        "Index": {'color': 'red'},
        "Name": {'color': 'magenta'},
    }
    table_show_manager.add_column(column_info)

    # Populate the table with episodes information
    for i, media in enumerate(obj_episode_manager):
        table_show_manager.add_tv_show({
            'Index': str(i+1),
            'Name': media.get('name'),
        })

    # Run the table and handle user input
    last_command = table_show_manager.run()

    if last_command == "q":
        console.print("\n[red]Quit [white]...")
        sys.exit(0)

    return last_command
