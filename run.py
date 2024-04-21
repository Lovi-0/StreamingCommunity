# 10.12.23 -> 31.01.24

import sys
import os
import logging
import platform
import argparse
from typing import Callable


# Internal utilities
from Src.Api import (
    get_version_and_domain, 
    download_series, 
    download_film, 
    search, 
    anime_search, 
    anime_download_series,
    anime_download_film,
    get_select_title
)
from Src.Util.message import start_message
from Src.Util.console import console, msg
from Src.Util.config import config_manager
from Src.Util._tmpConfig import temp_config_manager
from Src.Util._win32 import backup_path
from Src.Util.os import remove_folder, remove_file
from Src.Upload.update import update as git_update
from Src.Lib.FFmpeg import check_ffmpeg
from Src.Util.logger import Logger


# Config
DEBUG_MODE = config_manager.get_bool("DEFAULT", "debug")
DEBUG_GET_ALL_INFO = config_manager.get_bool('DEFAULT', 'get_info')
SWITCH_TO = config_manager.get_bool('DEFAULT', 'swith_anime')
CLOSE_CONSOLE =  config_manager.get_bool('DEFAULT', 'not_close')


def initialize(switch = False):
    """
    Initialize the application.
    Checks Python version, removes temporary folder, and displays start message.
    """

    # Set terminal size for win 7
    if platform.system() == "Windows" and "7" in platform.version():
        os.system('mode 120, 40')

    # Get system where script is run
    run_system = platform.system()
    

    # Enable debug with info
    if DEBUG_MODE:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('root').setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)
        logging.getLogger('root').setLevel(logging.ERROR)


    if sys.version_info < (3, 7):
        console.log("Install python version > 3.7.16")
        sys.exit(0)


    # Removing temporary folder
    remove_folder("tmp")
    remove_file("debug.log")
    start_message(switch)


    # Attempting GitHub update
    try:
        git_update()
    except Exception as e:
        console.print(f"[blue]Req github [white]=> [red]Failed: {e}")


    # Checking ffmpeg availability ( only win )
    if run_system == 'Windows':

        # Check if backup of path exist
        if not temp_config_manager.get_bool('Backup', 'path'):

            # Make backup of init path
            backup_path()
            temp_config_manager.add_variable('Backup', 'path', True)

        # Check if tmp config ffmpeg is present
        if not temp_config_manager.get_bool('Requirements', 'ffmpeg'):
            output_ffmpeg = check_ffmpeg()

            # If ffmpeg is present is win systems change config
            if output_ffmpeg:
                temp_config_manager.add_variable('Requirements', 'ffmpeg', True)


def main_film_series():
    """
    Main function of the application for film and series.
    """

    # Get site domain and version
    initialize()
    site_version, domain = get_version_and_domain()

    # Make request to site to get content that corrsisponde to that string
    film_search = msg.ask("\n[cyan]Insert word to search in all site: ").strip()
    len_database = search(film_search, domain)

    if len_database != 0:

        # Select title from list
        select_title = get_select_title()

        # For series
        if select_title.type == 'tv':
            download_series(
                tv_id=select_title.id,
                tv_name=select_title.slug, 
                version=site_version, 
                domain=domain
            )
        
        # For film
        else:
            download_film(
                id_film=select_title.id, 
                title_name=select_title.slug, 
                domain=domain
            )
    
    # If no media find
    else:
        console.print("[red]Cant find a single element")

    # End
    console.print("\n[red]Done")


def main_anime():
    """
    Main function of the application for anime unity
    """

    # Get site domain and version
    initialize(True)

    # Make request to site to get content that corrsisponde to that string
    film_search = msg.ask("\n[cyan]Insert word to search in all site: ").strip()
    len_database = anime_search(film_search)

    if len_database != 0:

        # Select title from list
        select_title = get_select_title(True)
        
        # For series
        if select_title.type == 'TV':
            anime_download_series(
                tv_id=select_title.id,
                tv_name=select_title.slug
            )
        
        # For film
        else:
            anime_download_film(
                id_film=select_title.id, 
                title_name=select_title.slug
            )

    # If no media find
    else:
        console.print("[red]Cant find a single element")


def run_function(func: Callable[..., None], close_console: bool = False) -> None:
    """
    Run a given function indefinitely or once, depending on the value of close_console.

    Parameters:
        func (Callable[..., None]): The function to run.
        close_console (bool, optional): Whether to close the console after running the function once. Defaults to False.
    """
    if close_console:
        while 1:
            func()
    else:
        func()


def main():

    # Create instance of logger
    logger = Logger()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Script to download film and series from internet.')
    parser.add_argument('-a', '--anime', action='store_true', help='Check into anime category')
    parser.add_argument('-f', '--film', action='store_true', help='Check into film/tv series category')
    args = parser.parse_args()

    if args.anime:
        run_function(main_anime, CLOSE_CONSOLE)

    elif args.film:
        run_function(main_film_series, CLOSE_CONSOLE)

    else:

        # If no arguments are provided, ask the user to input the category, if nothing insert return 0
        category = msg.ask("[cyan]Insert category [white]([red]0[white]: [bold magenta]Film/Series[white], [red]1[white]: [bold magenta]Anime[white])[white]:[/cyan]", choices={"0": "", "1": ""}, default="0")

        if category == '0':
            run_function(main_film_series, CLOSE_CONSOLE)

        elif category == '1':
            run_function(main_anime, CLOSE_CONSOLE)

        else:
            console.print("[red]Invalid category, you need to insert 0 or 1.")
            sys.exit(0)


if __name__ == '__main__':
    main()