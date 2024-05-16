# 3.12.23 -> 10.12.23

import os
import sys
import logging
from typing import List


# Internal utilities
from Src.Util.console import console, msg
from Src.Util.config import config_manager
from Src.Util.table import TVShowManager
from Src.Util.message import start_message
from Src.Util.os import remove_special_characters
from Src.Lib.Unidecode import transliterate
from Src.Util.file_validation import can_create_file
from Src.Lib.FFmpeg.my_m3u8 import Downloader
from Src.Util.mapper import map_episode_title
from .Class import VideoSource


# Config
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
SERIES_FOLDER = config_manager.get('DEFAULT', 'series_folder_name')
STREAM_SITE_NAME = config_manager.get('SITE', 'streaming_site_name')


# Variable
video_source = VideoSource()
video_source.set_url_base_name(STREAM_SITE_NAME)
table_show_manager = TVShowManager()


# --> LOGIC
def manage_selection(cmd_insert: str, max_count: int) -> List[int]:
    """
    Manage user selection for seasons to download.

    Args:
        cmd_insert (str): User input for season selection.
        max_count (int): Maximum count of seasons available.

    Returns:
        list_season_select (List[int]): List of selected seasons.
    """

    list_season_select = []

    # For a single number (e.g., '5')
    if cmd_insert.isnumeric():
        list_season_select.append(int(cmd_insert))

    # For a range (e.g., '[5-12]')
    elif "[" in cmd_insert:
        start, end = map(int, cmd_insert[1:-1].split('-'))
        list_season_select = list(range(start, end + 1))

    # For all seasons
    elif cmd_insert == "*":
        list_season_select = list(range(1, max_count+1))

    # Return list of selected seasons)
    return list_season_select


def display_episodes_list() -> str:
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
        "Duration": {'color': 'green'}
    }
    table_show_manager.add_column(column_info)

    # Populate the table with episodes information
    for i, media in enumerate(video_source.obj_episode_manager.episodes):
        table_show_manager.add_tv_show({
            'Index': str(media.number),
            'Name': media.name,
            'Duration': str(media.duration)
        })

    # Run the table and handle user input
    last_command = table_show_manager.run()

    if last_command == "q":
        console.print("\n[red]Quit [white]...")
        sys.exit(0)

    return last_command


# --> DOWNLOAD
def donwload_video(tv_name: str, index_season_selected: int, index_episode_selected: int) -> None:
    """
    Download a single episode video.

    Args:
        tv_name (str): Name of the TV series.
        index_season_selected (int): Index of the selected season.
        index_episode_selected (int): Index of the selected episode.
    """

    # Start message and display episode information
    start_message()
    console.print(f"[yellow]Download:  [red]{video_source.obj_episode_manager.episodes[index_episode_selected - 1].name} \n")
    episode_id = video_source.obj_episode_manager.episodes[index_episode_selected - 1].id

    # Define filename and path for the downloaded video
    mp4_name = f"{transliterate(remove_special_characters(map_episode_title(tv_name,video_source.obj_episode_manager.episodes[index_episode_selected - 1],index_season_selected)))}.mp4"
    mp4_path = remove_special_characters(os.path.join(ROOT_PATH, SERIES_FOLDER, tv_name, f"S{index_season_selected}"))
    os.makedirs(mp4_path, exist_ok=True)

    if not can_create_file(mp4_name):
        logging.error("Invalid mp4 name.")
        sys.exit(0)

    # Get iframe and content for the episode
    video_source.get_iframe(episode_id)
    video_source.get_content()
    video_source.set_url_base_name(STREAM_SITE_NAME)

    # Download the episode
    obj_download = Downloader(
        m3u8_playlist = video_source.get_playlist(),
        key = video_source.get_key(),
        output_filename = os.path.join(mp4_path, mp4_name)
    )

    obj_download.download_m3u8()



def donwload_episode(tv_name: str, index_season_selected: int, donwload_all: bool = False) -> None:
    """
    Download all episodes of a season.

    Args:
        tv_name (str): Name of the TV series.
        index_season_selected (int): Index of the selected season.
        donwload_all (bool): Donwload all seasons episodes
    """

    # Clean memory of all episodes and get the number of the season (some dont follow rule of [1,2,3,4,5] but [1,2,3,145,5,6,7]).
    video_source.obj_episode_manager.clear()
    season_number = (video_source.obj_title_manager.titles[index_season_selected-1].number)

    # Start message and collect information about episodes
    start_message()
    
    video_source.collect_title_season(season_number)
    episodes_count = video_source.obj_episode_manager.get_length()

    # Download all episodes wihtout ask
    if donwload_all:
        for i_episode in range(1, episodes_count+1):
            donwload_video(tv_name, index_season_selected, i_episode)

        console.print(f"\n[red]Download [yellow]season: [red]{index_season_selected}.")

    # If not download all episode but a single season
    if not donwload_all:

        # Display episodes list and manage user selection
        last_command = display_episodes_list()
        list_episode_select = manage_selection(last_command, episodes_count)

        # Download selected episodes
        if len(list_episode_select) == 1 and last_command != "*":
            donwload_video(tv_name, index_season_selected, list_episode_select[0])

        # Download all other episodes selecter
        else:
            for i_episode in list_episode_select:
                donwload_video(tv_name, index_season_selected, i_episode)


def download_series(tv_id: str, tv_name: str, version: str, domain: str) -> None:
    """
    Download all episodes of a TV series.

    Args:
        tv_id (str): ID of the TV series.
        tv_name (str): Name of the TV series.
        version (str): Version of the TV series.
        domain (str): Domain from which to download.
    """

    # Start message and set up video source
    start_message()
    video_source.set_version(version)
    video_source.set_domain(domain)
    video_source.set_series_name(tv_name)
    video_source.set_media_id(tv_id)

    # Collect information about seasons
    video_source.collect_info_seasons()
    seasons_count = video_source.obj_title_manager.get_length()

    # Prompt user for season selection and download episodes
    console.print(f"\n[green]Season found: [red]{seasons_count}")
    index_season_selected = str(msg.ask("\n[cyan]Insert media [red]index [yellow]or [red](*) [cyan]to download all media [yellow]or [red][1-2] [cyan]for a range of media"))
    list_season_select = manage_selection(index_season_selected, seasons_count)

    # Download selected episodes
    if len(list_season_select) == 1 and index_season_selected != "*":
        if 1 <= int(index_season_selected) <= seasons_count:
            donwload_episode(tv_name, list_season_select[0])

    # Dowload all seasons and episodes
    elif index_season_selected == "*":
        for i_season in list_season_select:
            donwload_episode(tv_name, i_season, True)

    # Download all other season selecter
    else:
        for i_season in list_season_select:
            donwload_episode(tv_name, i_season)
