# 3.12.23

import os
import sys
import time


# Internal utilities
from StreamingCommunity.Src.Util.console import console, msg
from StreamingCommunity.Src.Util.message import start_message
from StreamingCommunity.Src.Util.call_stack import get_call_stack
from StreamingCommunity.Src.Util.table import TVShowManager
from StreamingCommunity.Src.Lib.Downloader import HLS_Downloader


# Logic class
from .util.ScrapeSerie import ScrapeSerie
from StreamingCommunity.Src.Api.Template.Util import manage_selection, map_episode_title, validate_selection, validate_episode_selection, execute_search
from StreamingCommunity.Src.Api.Template.Class.SearchType import MediaItem


# Player
from StreamingCommunity.Src.Api.Player.vixcloud import VideoSource


# Variable
from .costant import ROOT_PATH, SITE_NAME, SERIES_FOLDER
scrape_serie = ScrapeSerie(SITE_NAME)
video_source = VideoSource(SITE_NAME, True)
table_show_manager = TVShowManager()



def download_video(tv_name: str, index_season_selected: int, index_episode_selected: int) -> None:
    """
    Download a single episode video.

    Parameters:
        - tv_name (str): Name of the TV series.
        - index_season_selected (int): Index of the selected season.
        - index_episode_selected (int): Index of the selected episode.
    """

    start_message()

    # Get info about episode
    obj_episode = scrape_serie.obj_episode_manager.episodes[index_episode_selected - 1]
    console.print(f"[yellow]Download: [red]{index_season_selected}:{index_episode_selected} {obj_episode.name}")
    print()

    # Define filename and path for the downloaded video
    mp4_name = f"{map_episode_title(tv_name, index_season_selected, index_episode_selected, obj_episode.name)}.mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, SERIES_FOLDER,  tv_name, f"S{index_season_selected}")

    # Retrieve scws and if available master playlist
    video_source.get_iframe(obj_episode.id)
    video_source.get_content()
    master_playlist = video_source.get_playlist()
    
    # Download the episode
    r_proc = HLS_Downloader(
        m3u8_playlist=master_playlist,
        output_filename=os.path.join(mp4_path, mp4_name)
    ).start()
    
    if r_proc == 404:
        time.sleep(2)

        # Re call search function
        if msg.ask("[green]Do you want to continue [white]([red]y[white])[green] or return at home[white]([red]n[white]) ", choices=['y', 'n'], default='y', show_choices=True) == "n":
            frames = get_call_stack()
            execute_search(frames[-4])

    if r_proc != None:
        console.print("[green]Result: ")
        console.print(r_proc)

def download_episode(tv_name: str, index_season_selected: int, download_all: bool = False) -> None:
    """
    Download episodes of a selected season.

    Parameters:
        - tv_name (str): Name of the TV series.
        - index_season_selected (int): Index of the selected season.
        - download_all (bool): Download all episodes in the season.
    """

    # Clean memory of all episodes and get the number of the season
    scrape_serie.obj_episode_manager.clear()
    season_number = scrape_serie.obj_season_manager.seasons[index_season_selected - 1].number

    # Start message and collect information about episodes
    start_message()
    scrape_serie.collect_title_season(season_number)
    episodes_count = scrape_serie.obj_episode_manager.get_length()

    if download_all:

        # Download all episodes without asking
        for i_episode in range(1, episodes_count + 1):
            download_video(tv_name, index_season_selected, i_episode)
        console.print(f"\n[red]End downloaded [yellow]season: [red]{index_season_selected}.")

    else:

        # Display episodes list and manage user selection
        last_command = display_episodes_list()
        list_episode_select = manage_selection(last_command, episodes_count)

        try:
            list_episode_select = validate_episode_selection(list_episode_select, episodes_count)
        except ValueError as e:
            console.print(f"[red]{str(e)}")
            return

        # Download selected episodes
        for i_episode in list_episode_select:
            download_video(tv_name, index_season_selected, i_episode)

def download_series(select_season: MediaItem, version: str) -> None:
    """
    Download episodes of a TV series based on user selection.

    Parameters:
        - select_season (MediaItem): Selected media item (TV series).
        - domain (str): Domain from which to download.
        - version (str): Version of the site.
    """

    # Start message and set up video source
    start_message()

    # Setup video source
    scrape_serie.setup(version, select_season.id, select_season.slug)
    video_source.setup(select_season.id)

    # Collect information about seasons
    scrape_serie.collect_info_seasons()
    seasons_count = scrape_serie.obj_season_manager.get_length()

    # Prompt user for season selection and download episodes
    console.print(f"\n[green]Seasons found: [red]{seasons_count}")
    index_season_selected = msg.ask(
        "\n[cyan]Insert season number [yellow](e.g., 1), [red]* [cyan]to download all seasons, "
        "[yellow](e.g., 1-2) [cyan]for a range of seasons, or [yellow](e.g., 3-*) [cyan]to download from a specific season to the end"
    )
    
    # Manage and validate the selection
    list_season_select = manage_selection(index_season_selected, seasons_count)

    try:
        list_season_select = validate_selection(list_season_select, seasons_count)
    except ValueError as e:
        console.print(f"[red]{str(e)}")
        return

    # Loop through the selected seasons and download episodes
    for i_season in list_season_select:
        if len(list_season_select) > 1 or index_season_selected == "*":

            # Download all episodes if multiple seasons are selected or if '*' is used
            download_episode(select_season.slug, i_season, download_all=True)
        else:

            # Otherwise, let the user select specific episodes for the single season
            download_episode(select_season.slug, i_season, download_all=False)


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
    for i, media in enumerate(scrape_serie.obj_episode_manager.episodes):
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
