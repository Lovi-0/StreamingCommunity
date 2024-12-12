# 03.03.24

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.style import Style
from typing import Dict, List, Any


# Internal utilities
from .message import start_message


class TVShowManager:
    def __init__(self):
        """
        Initialize TVShowManager with provided column information.

        Parameters:
            - column_info (Dict[str, Dict[str, str]]): Dictionary containing column names, their colors, and justification.
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

        self.console.print(table)  # Use self.console.print instead of print


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

        while True:
            start_message()

            # Display table
            self.display_data(self.tv_shows[self.slice_start:self.slice_end])

            # Handling user input for loading more items or quitting
            if self.slice_end < total_items:
                self.console.print(f"\n\n[yellow][INFO] [green]Press [red]Enter [green]for next page, or [red]'q' [green]to quit.")

                if not force_int_input:
                    key = Prompt.ask(
                        "\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                        "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end"
                    )
                    
                else:
                    choices = [str(i) for i in range(0, max_int_input)]
                    choices.extend(["q", ""])

                    key = Prompt.ask("[cyan]Insert media [red]index", choices=choices, show_choices=False)
                last_command = key

                if key.lower() == "q":
                    break

                elif key == "":
                    self.slice_start += self.step
                    self.slice_end += self.step
                    if self.slice_end > total_items:
                        self.slice_end = total_items

                else:
                    break

            else:
                # Last slice, ensure all remaining items are shown
                self.console.print(f"\n\n[yellow][INFO] [red]You've reached the end. [green]Press [red]Enter [green]for next page, or [red]'q' [green]to quit.")
                if not force_int_input:
                    key = Prompt.ask(
                        "\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                        "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end"
                    )


                else:
                    choices = [str(i) for i in range(0, max_int_input)]
                    choices.extend(["q", ""])

                    key = Prompt.ask("[cyan]Insert media [red]index", choices=choices, show_choices=False)
                last_command = key

                if key.lower() == "q":
                    break

                elif key == "":
                    self.slice_start = 0
                    self.slice_end = self.step

                else:
                    break
            
        return last_command

    def clear(self):
        self.tv_shows = []
