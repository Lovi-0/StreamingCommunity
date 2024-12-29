# 10.12.23

import os
import sys
import time
import glob
import logging
import platform
import argparse
import importlib
from typing import Callable
from rich.console import Console

# Internal utilities
from StreamingCommunity.Util.message import start_message
from StreamingCommunity.Util.console import console, msg
from StreamingCommunity.Util._jsonConfig import config_manager
from StreamingCommunity.Upload.update import update as git_update
from StreamingCommunity.Util.os import os_summary
from StreamingCommunity.Util.logger import Logger
from StreamingCommunity.Api.Template.Class.SearchType import MediaManager
from StreamingCommunity.Api.Template import get_select_title
from StreamingCommunity.Util.table import TVShowManager

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
    """
    Load search functions from modules in the 'Api/Site' directory.

    Returns:
        Dict[str, Tuple[Callable[..., Any], str]]: A dictionary where keys are module aliases and values are tuples
        containing the search function and its usage category.
    """
    modules = []
    loaded_functions = {}

    if getattr(sys, 'frozen', False):
        base_path = os.path.join(sys._MEIPASS, "StreamingCommunity")
    else:
        base_path = os.path.dirname(__file__)

    api_dir = os.path.join(base_path, 'Api', 'Site')
    init_files = glob.glob(os.path.join(api_dir, '*', '__init__.py'))

    for init_file in init_files:
        module_name = os.path.basename(os.path.dirname(init_file))
        logging.info(f"Load module name: {module_name}")

        try:
            mod = importlib.import_module(f'StreamingCommunity.Api.Site.{module_name}')
            indice = getattr(mod, 'indice', 0)
            is_deprecate = bool(getattr(mod, '_deprecate', True))
            use_for = getattr(mod, '_useFor', 'other')

            if not is_deprecate:
                modules.append((module_name, indice, use_for))

        except Exception as e:
            console.print(f"[red]Failed to import module {module_name}: {str(e)}")

    modules.sort(key=lambda x: x[1])

    for module_name, _, use_for in modules:
        module_alias = f'{module_name}_search'

        try:
            mod = importlib.import_module(f'StreamingCommunity.Api.Site.{module_name}')
            search_function = getattr(mod, 'search')
            loaded_functions[module_alias] = (search_function, use_for)

        except Exception as e:
            console.print(f"[red]Failed to load search function from module {module_name}: {str(e)}")

    return loaded_functions


def search_all_sites(loaded_functions, search_string, max_sites=10):
    """
    Search all sites for the given search string and display results.

    Parameters:
        loaded_functions (Dict[str, Tuple[Callable[..., Any], str]]): Dictionary of loaded search functions and their usage categories.
        search_string (str): The search string to use for querying the sites.
        max_sites (int, optional): The maximum number of sites to search. Defaults to 10.

    Returns:
        int: The total number of results found across all sites.
    """
    total_len_database = 0
    site_count = 0
    console = Console()
    managers = []

    for module_alias, (search_function, use_for) in loaded_functions.items():
        if max_sites is not None and site_count >= max_sites:
            break

        console.print(f"\n[blue]Searching in module: {module_alias} [white](Use for: {use_for})")

        try:
            database: MediaManager = search_function(search_string, get_onylDatabase=True)
            len_database = len(database.media_list)
            if len_database > 0:
                table_show_manager = TVShowManager(console=console, global_search=True)
                managers.append(table_show_manager)
                selected_media = get_select_title(table_show_manager, database)
                console.print(f"[green]Selected media: {selected_media}")

            console.print(f"[green]Database length for {module_alias}: {len_database}")
            total_len_database += len_database
            site_count += 1

        except Exception as e:
            console.print(f"[red]Error while executing search function for {module_alias}: {str(e)}")

    if not managers:
        console.print("[red]No results found in any site.")
        return total_len_database

    manager_index = 0
    while True:
        command = managers[manager_index].run(global_search=True)
        if command == "next":
            manager_index = (manager_index + 1) % len(managers)
        elif command == "prev":
            manager_index = (manager_index - 1) % len(managers)
        elif command == "quit":
            break
        elif command.isdigit() and int(command) < len(managers[manager_index].media_list):
            selected_media = managers[manager_index].media_list[int(command)]
            console.print(f"[green]Selected media: {selected_media}")
            break
        else:
            console.print("[red]Invalid command. Please enter 'next', 'prev', 'quit', or a valid index.")

    return total_len_database



def initialize():
    """
    Initialize the application by displaying the start message, getting the system summary,
    setting the console mode for Windows 7, checking the Python version, and updating from GitHub.

    Raises:
        SystemExit: If the Python version is less than 3.7.16.
    """
    start_message()
    os_summary.get_system_summary()

    if platform.system() == "Windows" and "7" in platform.version():
        os.system('mode 120, 40')

    if sys.version_info < (3, 7):
        console.log("[red]Install python version > 3.7.16")
        sys.exit(0)

    try:
        git_update()
        print()
    except:
        console.log("[red]Error with loading github.")


def main():
    start = time.time()
    log_not = Logger()
    initialize()

    search_functions = load_search_functions()
    logging.info(f"Load module in: {time.time() - start} s")

    parser = argparse.ArgumentParser(description='Script to download film and series from the internet.')
    color_map = {
        "anime": "red",
        "film_serie": "yellow",
        "film": "blue",
        "serie": "green",
        "other": "white"
    }

    for alias, (_, use_for) in search_functions.items():
        short_option = alias[:3].upper()
        long_option = alias
        parser.add_argument(f'-{short_option}', f'--{long_option}', action='store_true',
                            help=f'Search for {alias.split("_")[0]} on streaming platforms.')

    parser.add_argument('-G', '--global_search', action='store_true', help='Perform a global search across all sites.')
    parser.add_argument('search_string', type=str, nargs='?', default='', help='Search string for global search.')

    args = parser.parse_args()
    arg_to_function = {alias: func for alias, (func, _) in search_functions.items()}

    if args.global_search:
        total_len = search_all_sites(search_functions, args.search_string)
        console.print(f"\n[cyan]Total number of results from all sites: {total_len}")
        return

    for arg, func in arg_to_function.items():
        if getattr(args, arg):
            run_function(func)
            return

    input_to_function = {str(i): func for i, (alias, (func, _)) in enumerate(search_functions.items())}
    choice_labels = {str(i): (alias.split("_")[0].capitalize(), use_for) for i, (alias, (_, use_for)) in
                     enumerate(search_functions.items())}
    legend_text = " | ".join([f"[{color}]{category.capitalize()}[/{color}]" for category, color in color_map.items()])
    console.print(f"\n[bold green]Category Legend:[/bold green] {legend_text}")

    prompt_message = "[green]Insert category [white](" + ", ".join(
        [f"{key}: [{color_map[label[1]]}]{label[0]}[/{color_map[label[1]]}]" for key, label in choice_labels.items()]
    ) + ", G: Global Search[white])"

    category = msg.ask(prompt_message, choices=list(choice_labels.keys()) + ['G', 'g', '*'], default="0", show_choices=False,
                       show_default=False)

    if category in input_to_function:
        run_function(input_to_function[category])
    elif category in ['G', 'g', '*']:
        search_string = msg.ask("[green]Insert word to search globally:")
        total_len = search_all_sites(search_functions, search_string)
        console.print(f"\n[cyan]Total number of results from all sites: {total_len}")
    else:
        console.print("[red]Invalid category.")
        sys.exit(0)


if __name__ == "__main__":
    main()