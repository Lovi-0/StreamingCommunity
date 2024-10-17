# 11.03.24

import os
import sys
import logging


# Internal utilities
from Src.Util.console import console, msg
from Src.Util.message import start_message
from Src.Util.os import create_folder, can_create_file
from Src.Lib.Downloader import MP4_downloader


# Logic class
from ..Template import manage_selection
from ..Template.Class.SearchType import MediaItem
from .Core.Player.vixcloud import VideoSource


# Variable
from .costant import ROOT_PATH, SITE_NAME, SERIES_FOLDER, MOVIE_FOLDER
video_source = VideoSource()


def download_episode(index_select: int):
    """
    Downloads the selected episode.

    Parameters:
        - index_select (int): Index of the episode to download.
    """

    # Get information about the selected episode
    obj_episode = video_source.get_info_episode(index_select)

    if obj_episode is not None:

        start_message()
        console.print(f"[yellow]Download:  [red]EP_{obj_episode.number} \n")

        # Get the js script from the episode
        js_script = video_source.get_embed(obj_episode.id)

        # Parse parameter in embed text
        video_source.parse_script(js_script)

        # Create output path
        mp4_path = None
        mp4_name = f"{obj_episode.number}.mp4"
        if video_source.is_series:
            mp4_path = os.path.join(ROOT_PATH, SITE_NAME, SERIES_FOLDER, video_source.series_name)
        else:
            mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, video_source.series_name)

        # Check if can create file output
        create_folder(mp4_path)                                                                    
        if not can_create_file(mp4_name):  
            logging.error("Invalid mp4 name.")
            sys.exit(0)

        # Start downloading
        MP4_downloader(
            str(video_source.src_mp4).strip(),
            os.path.join(mp4_path, mp4_name)
        )

    else:
        logging.error(f"Skip index: {index_select} cant find info with api.")


def download_series(select_title: MediaItem):
    """
    Function to download episodes of a TV series.

    Parameters:
        - tv_id (int): The ID of the TV series.
        - tv_name (str): The name of the TV series.
    """

    # Set up video source
    video_source.setup(select_title.id, select_title.slug)

    # Get the count of episodes for the TV series
    episoded_count = video_source.get_count_episodes()
    console.log(f"[cyan]Episodes find: [red]{episoded_count}")

    # Prompt user to select an episode index
    last_command = msg.ask("\n[cyan]Insert media [red]index [yellow]or [red](*) [cyan]to download all media [yellow]or [red][1-2] [cyan]or [red][3-*] [cyan]for a range of media")

    # Manage user selection
    list_episode_select = manage_selection(last_command, episoded_count)

    # Download selected episodes
    if len(list_episode_select) == 1 and last_command != "*":
        download_episode(list_episode_select[0]-1)

    # Download all other episodes selecter
    else:
        for i_episode in list_episode_select:
            download_episode(i_episode-1)


def download_film(select_title: MediaItem):
    """
    Function to download a film.

    Parameters:
        - id_film (int): The ID of the film.
        - title_name (str): The title of the film.
    """

    # Set up video source
    video_source.setup(select_title.id, select_title.slug)
    video_source.is_series = False

    # Start download
    download_episode(0)
