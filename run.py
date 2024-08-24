# 10.12.23

import os
import sys
import glob
import logging
import platform
import argparse
import importlib

from typing import Callable


# Internal utilities
from Src.Util.message import start_message
from Src.Util.console import console, msg
from Src.Util._jsonConfig import config_manager
from Src.Upload.update import update as git_update
from Src.Util.os import get_system_summary
from Src.Lib.TMBD.tmbd import tmdb
from Src.Util.logger import Logger


# Config
CLOSE_CONSOLE = config_manager.get_bool('DEFAULT', 'not_close')



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



def load_search_functions():

    modules = []
    loaded_functions = {}

    # Traverse the Api directory
    api_dir = os.path.join(os.path.dirname(__file__), 'Src', 'Api')
    init_files = glob.glob(os.path.join(api_dir, '*', '__init__.py'))
    
    logging.info(f"Base folder path: {api_dir}")
    logging.info(f"Api module path: {init_files}")


    # Retrieve modules and their indices
    for init_file in init_files:

        # Get folder name as module name
        module_name = os.path.basename(os.path.dirname(init_file))
        logging.info(f"Load module name: {module_name}")

        try:
            # Dynamically import the module
            mod = importlib.import_module(f'Src.Api.{module_name}')

            # Get 'indice' from the module
            indice = getattr(mod, 'indice', 0)
            is_deprecate = bool(getattr(mod, '_deprecate', True))

            # Add module and indice to the list
            if not is_deprecate:
                modules.append((module_name, indice))

        except Exception as e:
            console.print(f"[red]Failed to import module {module_name}: {str(e)}")

    # Sort modules by 'indice'
    modules.sort(key=lambda x: x[1])

    # Load search functions in the sorted order
    for module_name, _ in modules:

        # Construct a unique alias for the module
        module_alias = f'{module_name}_search'
        logging.info(f"Module alias: {module_alias}")

        try:
            # Dynamically import the module
            mod = importlib.import_module(f'Src.Api.{module_name}')

            # Get the search function from the module (assuming the function is named 'search' and defined in __init__.py)
            search_function = getattr(mod, 'search')

            # Add the function to the loaded functions dictionary
            loaded_functions[module_alias] = search_function

        except Exception as e:
            console.print(f"[red]Failed to load search function from module {module_name}: {str(e)}")

    return loaded_functions



def initialize():

    # Get start message
    start_message()

    # Create logger
    log_not = Logger()

    # Get system info
    get_system_summary()

    # Set terminal size for win 7
    if platform.system() == "Windows" and "7" in platform.version():
        os.system('mode 120, 40')

    # Check python version
    if sys.version_info < (3, 7):
        console.log("[red]Install python version > 3.7.16")
        sys.exit(0)

    # Attempting GitHub update
    try:
        git_update()
        print()
    except:
        console.log("[red]Error with loading github.")

    # Show trending film and series
    tmdb.display_trending_films()
    tmdb.display_trending_tv_shows()
    

def main():

    # Load search functions
    search_functions = load_search_functions()

    # Create dynamic argument parser
    parser = argparse.ArgumentParser(description='Script to download film and series from the internet.')

    # Add dynamic arguments based on loaded search modules
    for alias in search_functions.keys():
        short_option = alias[:3].upper()                # Take the first three letters of the alias in uppercase
        long_option = alias                             # Use the full alias as the full option name
        parser.add_argument(f'-{short_option}', f'--{long_option}', action='store_true', help=f'Search for {alias.split("_")[0]} on streaming platforms.')

    # Parse command line arguments
    args = parser.parse_args()

    # Mapping command-line arguments to functions
    arg_to_function = {alias: search_functions[alias] for alias in search_functions.keys()}

    # Check which argument is provided and run the corresponding function
    for arg, func in arg_to_function.items():
        if getattr(args, arg):
            run_function(func)
            return

    # Mapping user input to functions
    input_to_function = {str(i): search_functions[alias] for i, alias in enumerate(search_functions.keys())}

    # Create dynamic prompt message and choices
    choice_labels = {str(i): alias.split("_")[0].capitalize() for i, alias in enumerate(search_functions.keys())}
    prompt_message = f"[green]Insert category [white]({', '.join([f'[red]{key}: [magenta]{label}' for key, label in choice_labels.items()])}[white]): "

    # Ask the user for input
    category = msg.ask(prompt_message, choices=list(choice_labels.keys()), default="0")

    # Run the corresponding function based on user input
    if category in input_to_function:
        run_function(input_to_function[category])
    else:
        console.print("[red]Invalid category.")
        sys.exit(0)



if __name__ == '__main__':
    initialize()
    main()