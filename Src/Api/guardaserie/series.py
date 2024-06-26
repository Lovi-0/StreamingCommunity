# 13.06.24

import os
import sys
import logging


# Internal utilities
from Src.Util.console import console, msg
from Src.Util.table import TVShowManager
from Src.Util.message import start_message
from Src.Lib.Downloader import HLS_Downloader
from ..Template import manage_selection, map_episode_title


# Logic class
from .Core.Class.SearchType import MediaItem
from .Core.Class.ScrapeSerie import GetSerieInfo
from .Core.Player.supervideo import VideoSource


# Variable
from .costant import ROOT_PATH, SITE_NAME, SERIES_FOLDER
table_show_manager = TVShowManager()
video_source = VideoSource()



def donwload_video(scape_info_serie: GetSerieInfo, index_season_selected: int, index_episode_selected: int) -> None:
    """
    Download a single episode video.

    Args:
        - tv_name (str): Name of the TV series.
        - index_season_selected (int): Index of the selected season.
        - index_episode_selected (int): Index of the selected episode.
    """

    start_message()

    # Get info about episode
    obj_episode = scape_info_serie.list_episodes[index_episode_selected - 1]
    console.print(f"[yellow]Download: [red]{index_season_selected}:{index_episode_selected} {obj_episode.get('name')}")
    print()

    # Define filename and path for the downloaded video
    mp4_name = f"{map_episode_title(scape_info_serie.tv_name, index_season_selected, index_episode_selected, obj_episode.get('name'))}.mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, SERIES_FOLDER, scape_info_serie.tv_name, f"S{index_season_selected}")

    # Setup video source
    video_source.setup(obj_episode.get('url'))

    # Get m3u8 master playlist
    master_playlist = video_source.get_playlist()
    
    HLS_Downloader(
        m3u8_playlist = master_playlist,
        output_filename = os.path.join(mp4_path, mp4_name)
    ).start()


def donwload_episode(scape_info_serie: GetSerieInfo, index_season_selected: int, donwload_all: bool = False) -> None:
    """
    Download all episodes of a season.

    Args:
        - tv_name (str): Name of the TV series.
        - index_season_selected (int): Index of the selected season.
        - donwload_all (bool): Donwload all seasons episodes
    """

    # Start message and collect information about episodes
    start_message()
    list_dict_episode = scape_info_serie.get_episode_number(index_season_selected)
    episodes_count = len(list_dict_episode)

    # Download all episodes wihtout ask
    if donwload_all:
        for i_episode in range(1, episodes_count+1):
            donwload_video(scape_info_serie, index_season_selected, i_episode)

        console.print(f"\n[red]Download [yellow]season: [red]{index_season_selected}.")

    # If not download all episode but a single season
    if not donwload_all:

        # Display episodes list and manage user selection
        last_command = display_episodes_list(scape_info_serie.list_episodes)
        list_episode_select = manage_selection(last_command, episodes_count)

        # Download selected episodes
        if len(list_episode_select) == 1 and last_command != "*":
            donwload_video(scape_info_serie, index_season_selected, list_episode_select[0])

        # Download all other episodes selecter
        else:
            for i_episode in list_episode_select:
                donwload_video(scape_info_serie, index_season_selected, i_episode)


def download_series(dict_serie: MediaItem) -> None:
    """
    Download all episodes of a TV series.

    Parameter:
        - dict_serie (MediaItem): obj with url name type and score
    """

    # Start message and set up video source
    start_message()

    # Init class
    scape_info_serie = GetSerieInfo(dict_serie)

    # Collect information about seasons
    seasons_count = scape_info_serie.get_seasons_number()

    # Prompt user for season selection and download episodes
    console.print(f"\n[green]Season find: [red]{seasons_count}")
    index_season_selected = str(msg.ask("\n[cyan]Insert media [red]index [yellow]or [red](*) [cyan]to download all media [yellow]or [red][1-2] [cyan]for a range of media"))
    list_season_select = manage_selection(index_season_selected, seasons_count)

    # Download selected episodes
    if len(list_season_select) == 1 and index_season_selected != "*":
        if 1 <= int(index_season_selected) <= seasons_count:
            donwload_episode(scape_info_serie, list_season_select[0])

    # Dowload all seasons and episodes
    elif index_season_selected == "*":
        for i_season in list_season_select:
            donwload_episode(scape_info_serie, i_season, True)

    # Download all other season selecter
    else:
        for i_season in list_season_select:
            donwload_episode(scape_info_serie, i_season)


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
    for media in obj_episode_manager:
        table_show_manager.add_tv_show({
            'Index': str(media.get('number')),
            'Name': media.get('name'),
        })

    # Run the table and handle user input
    last_command = table_show_manager.run()

    if last_command == "q":
        console.print("\n[red]Quit [white]...")
        sys.exit(0)

    return last_command
