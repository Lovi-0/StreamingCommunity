# 03.03.24

import os
import sys
import logging
import importlib


# External library
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.style import Style
from typing import Dict, List, Any


# Internal utilities
from .message import start_message
from .call_stack import get_call_stack

# Telegram bot instance
from StreamingCommunity.TelegramHelp.telegram_bot import get_bot_instance
from StreamingCommunity.Util._jsonConfig import config_manager
TELEGRAM_BOT = config_manager.get_bool('DEFAULT', 'telegram_bot')


class TVShowManager:
    def __init__(self):
        """
        Initialize TVShowManager with provided column information.
        """
        self.console = Console()
        self.tv_shows: List[Dict[str, Any]] = []  # List to store TV show data as dictionaries
        self.slice_start: int = 0
        self.slice_end: int = 5
        self.step: int = self.slice_end
        self.column_info = []

    def set_slice_end(self, new_slice: int) -> None:
        """
        Set the end of the slice for displaying TV shows.

        Parameters:
            - new_slice (int): The new value for the slice end.
        """
        self.slice_end = new_slice
        self.step = new_slice

    def add_column(self, column_info: Dict[str, Dict[str, str]]) -> None:
        """
        Add column information.
    
        Parameters:
            - column_info (Dict[str, Dict[str, str]]): Dictionary containing column names, their colors, and justification.
        """
        self.column_info = column_info

    def add_tv_show(self, tv_show: Dict[str, Any]):
        """
        Add a TV show to the list of TV shows.

        Parameters:
            - tv_show (Dict[str, Any]): Dictionary containing TV show details.
        """
        self.tv_shows.append(tv_show)

    def display_data(self, data_slice: List[Dict[str, Any]]):
        """
        Display TV show data in a tabular format.

        Parameters:
            - data_slice (List[Dict[str, Any]]): List of dictionaries containing TV show details to display.
        """
        table = Table(border_style="white")

        # Add columns dynamically based on provided column information
        for col_name, col_style in self.column_info.items():
            color = col_style.get("color", None)
            if color:
                style = Style(color=color)
            else:
                style = None
            table.add_column(col_name, style=style, justify='center')

        # Add rows dynamically based on available TV show data
        for entry in data_slice:
            # Create row data while handling missing keys
            row_data = [entry.get(col_name, '') for col_name in self.column_info.keys()]
            table.add_row(*row_data)

        self.console.print(table)

    def run_back_command(self, research_func: dict):
        """
        Executes a back-end search command by dynamically importing a module and invoking its search function.

        Args:
            research_func (dict): A dictionary containing:
                - 'folder' (str): The absolute path to the directory containing the module to be executed.
        """
        try:

            # Get site name from folder
            site_name = (os.path.basename(research_func['folder']))

            # Find the project root directory
            current_path = research_func['folder']
            while not os.path.exists(os.path.join(current_path, 'StreamingCommunity')):
                current_path = os.path.dirname(current_path)
            
            # Add project root to Python path
            project_root = current_path
            #print(f"[DEBUG] Project Root: {project_root}")
            
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Import using full absolute import
            module_path = f'StreamingCommunity.Api.Site.{site_name}'
            #print(f"[DEBUG] Importing module: {module_path}")
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the search function
            search_func = getattr(module, 'search')
            
            # Call the search function with the search string
            search_func(None)
            
        except Exception as e:
            self.console.print(f"[red]Error during search: {e}")
            
            # Print detailed traceback
            import traceback
            traceback.print_exc()
        
        # Optionally remove the path if you want to clean up
        if project_root in sys.path:
            sys.path.remove(project_root)


    def run(self, force_int_input: bool = False, max_int_input: int = 0) -> str:
        """
        Run the TV show manager application.

        Parameters:
            - force_int_input(bool): If True, only accept integer inputs from 0 to max_int_input
            - max_int_input (int): range of row to show
        
        Returns:
            str: Last command executed before breaking out of the loop.
        """
        total_items = len(self.tv_shows)
        last_command = ""  # Variable to store the last command executed

        if TELEGRAM_BOT:
          bot = get_bot_instance()
          
        while True:
            start_message()

            # Display table
            self.display_data(self.tv_shows[self.slice_start:self.slice_end])

            # Find research function from call stack
            research_func = None
            for reverse_fun in get_call_stack():
                if reverse_fun['function'] == 'search' and reverse_fun['script'] == '__init__.py':
                    research_func = reverse_fun
                    logging.info(f"Found research_func: {research_func}")

            # Handling user input for loading more items or quitting
            if self.slice_end < total_items:
                self.console.print(f"\n[green]Press [red]Enter [green]for next page, [red]'q' [green]to quit, or [red]'back' [green]to search.")

                if not force_int_input:
                    if TELEGRAM_BOT:
                      self.console.print(f"\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                          "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end")
                      key = bot.ask(
                          "select_title_episode",
                          f"Inserisci l'indice dei media (ad esempio, 1), * per scaricare tutti i media, (ad esempio, 1-2) per un intervallo di media, o (ad esempio, 3-*) per scaricare dal un indice specifico fino alla fine.",
                          None
                      )
                    else:
                      key = Prompt.ask(
                        "\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                        "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end"
                    )
                    
                else:
                    choices = [str(i) for i in range(0, max_int_input)]
                    choices.extend(["q", "quit", "b", "back"])
                    if TELEGRAM_BOT:
                      self.console.print(f"[cyan]Insert media [red]index")
                      key = bot.ask(
                        "select_title",
                        f"Scegli il contenuto da scaricare:\n📺 Serie TV - 🎞️ Film - 🌀 Anime\noppure `back` per tornare indietro",
                        None
                      )
                    else:
                      key = Prompt.ask("[cyan]Insert media [red]index", choices=choices, show_choices=False)
                        
                last_command = key

                if key.lower() == "q" or key.lower() == "quit":
                    break

                elif key == "":
                    self.slice_start += self.step
                    self.slice_end += self.step
                    if self.slice_end > total_items:
                        self.slice_end = total_items

                elif (key.lower() == "b" or key.lower() == "back") and research_func:
                    self.run_back_command(research_func)

                else:
                    break

            else:
                # Last slice, ensure all remaining items are shown
                self.console.print(f"\n [green]You've reached the end. [red]Enter [green]for first page, [red]'q' [green]to quit, or [red]'back' [green]to search.")
                if not force_int_input:
                    if TELEGRAM_BOT:
                      self.console.print(f"\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                          "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end")
                      key = bot.ask(
                          "select_title_episode",
                          f"Inserisci l'indice dei media (ad esempio, 1), * per scaricare tutti i media, (ad esempio, 1-2) per un intervallo di media, o (ad esempio, 3-*) per scaricare dal un indice specifico fino alla fine.",
                          None
                      )
                    else:
                      key = Prompt.ask(
                          "\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                          "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end"
                      )

                else:
                    choices = [str(i) for i in range(0, max_int_input)]
                    choices.extend(["q", "quit", "b", "back"])

                    if TELEGRAM_BOT:
                      self.console.print(f"[cyan]Insert media [red]index")
                      key = bot.ask(
                        "select_title",
                        f"Scegli il contenuto da scaricare:\n📺 Serie TV - 🎞️ Film - 🌀 Anime\n oppure `back` per tornare indietro",
                        None
                      )
                    else:
                      key = Prompt.ask("[cyan]Insert media [red]index", choices=choices, show_choices=False)
                        
                last_command = key

                if key.lower() == "q" or key.lower() == "quit":
                    break

                elif key == "":
                    self.slice_start = 0
                    self.slice_end = self.step

                elif (key.lower() == "b" or key.lower() == "back") and research_func:
                    self.run_back_command(research_func)

                else:
                    break
            
        return last_command

    def clear(self):
        self.tv_shows = []