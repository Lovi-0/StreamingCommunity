# 10.12.23 -> 31.01.24

import sys
import logging
import platform


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


def initialize():
    """
    Initialize the application.
    Checks Python version, removes temporary folder, and displays start message.
    """

    # Get system where script is run
    run_system = platform.system()
    

    # Enable debug with info
    if DEBUG_MODE:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('root').setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)
        logging.getLogger('root').setLevel(logging.ERROR)


    if sys.version_info < (3, 11):
        console.log("Install python version > 3.11")
        sys.exit(0)


    # Removing temporary folder
    remove_folder("tmp")
    remove_file("debug.log")
    start_message()


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


def main():
    """
    Main function of the application.
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


def main_switch():
    """
    Main function for anime unity
    """

    # Get site domain and version
    initialize()

    # Make request to site to get content that corrsisponde to that string
    film_search = msg.ask("\n[cyan]Insert word to search in all site: ").strip()
    len_database = anime_search(film_search)

    if len_database != 0:

        # Select title from list
        select_title = get_select_title()
        
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


if __name__ == '__main__':

    logger = Logger()

    if not SWITCH_TO:
        if not CLOSE_CONSOLE:
            main()
        else:
            while 1:
                main()

    else:
        if not CLOSE_CONSOLE:
            main_switch()
        else:
            while 1:
                main_switch()
