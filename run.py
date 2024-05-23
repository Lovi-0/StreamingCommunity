# 10.12.23

import sys
import os
import platform
import argparse
import logging
from typing import Callable


# Internal utilities
from Src.Util.message import start_message
from Src.Util.console import console, msg
from Src.Util._jsonConfig import config_manager
from Src.Util._tmpConfig import temp_config_manager
from Src.Upload.update import update as git_update
from Src.Lib.FFmpeg import check_ffmpeg
from Src.Util.logger import Logger

# Internal api
from Src.Api.Streamingcommunity import main_film_series
from Src.Api.Animeunity import main_anime


# Config
CLOSE_CONSOLE = config_manager.get_bool('DEFAULT', 'not_close')


def initialize(switch = False):
    """
    Initialize the application.
    Checks Python version, removes temporary folder, and displays start message.
    """

    # Set terminal size for win 7
    if platform.system() == "Windows" and "7" in platform.version():
        os.system('mode 120, 40')


    # Check python version
    if sys.version_info < (3, 7):
        console.log("[red]Install python version > 3.7.16")
        sys.exit(0)


    # Removing temporary folder
    start_message(switch)


    # Attempting GitHub update
    try:
        git_update()
    except Exception as e:
        console.print(f"[blue]Req github [white]=> [red]Failed: {e}")


    # Check if tmp config ffmpeg is present
    if not temp_config_manager.get_bool('Setting', 'ffmpeg'):
        output_ffmpeg = check_ffmpeg()

        # If ffmpeg is present is win systems change config
        if output_ffmpeg:
            temp_config_manager.add_variable('Setting', 'ffmpeg', True)
        
        else:
            logging.error("FFmpeg not exist")

    else:
        logging.info("FFmpeg exist")


def run_function(func: Callable[..., None], close_console: bool = False) -> None:
    """
    Run a given function indefinitely or once, depending on the value of close_console.

    Parameters:
        func (Callable[..., None]): The function to run.
        close_console (bool, optional): Whether to close the console after running the function once. Defaults to False.
    """
    
    initialize()

    if close_console:
        while 1:
            func()
    else:
        func()


def main():

    log_not = Logger()

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