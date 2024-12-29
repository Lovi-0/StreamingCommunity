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


class TVShowManager:
    def __init__(self, console=Console(), global_search=False):
        self.isGlobal = global_search
        self.console = console
        self.tv_shows: List[Dict[str, Any]] = []
        self.slice_start: int = 0
        self.slice_end: int = 5
        self.step: int = self.slice_end
        self.column_info = []

    def set_slice_end(self, new_slice: int) -> None:
        self.slice_end = new_slice
        self.step = new_slice

    def add_column(self, column_info: Dict[str, Dict[str, str]]) -> None:
        self.column_info = column_info

    def add_tv_show(self, tv_show: Dict[str, Any]):
        self.tv_shows.append(tv_show)

    def display_data(self, data_slice: List[Dict[str, Any]]):
        table = Table(border_style="white")
        for col_name, col_style in self.column_info.items():
            color = col_style.get("color", None)
            style = Style(color=color) if color else None
            table.add_column(col_name, style=style, justify='center')
        for entry in data_slice:
            row_data = [entry.get(col_name, '') for col_name in self.column_info.keys()]
            table.add_row(*row_data)
        self.console.print(table)

    def run_back_command(self, research_func: dict):
        try:
            site_name = os.path.basename(research_func['folder'])
            current_path = research_func['folder']
            while not os.path.exists(os.path.join(current_path, 'StreamingCommunity')):
                current_path = os.path.dirname(current_path)
            project_root = current_path
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            module_path = f'StreamingCommunity.Api.Site.{site_name}'
            module = importlib.import_module(module_path)
            search_func = getattr(module, 'search')
            search_func(None)
        except Exception as e:
            self.console.print(f"[red]Error during search: {e}")
            import traceback
            traceback.print_exc()
        if project_root in sys.path:
            sys.path.remove(project_root)
    '''
    def run(self, force_int_input: bool = False, max_int_input: int = 0) -> str:
        total_items = len(self.tv_shows)
        last_command = ""
        while True:
            start_message()
            self.display_data(self.tv_shows[self.slice_start:self.slice_end])
            research_func = None
            for reverse_fun in get_call_stack():
                if reverse_fun['function'] == 'search' and reverse_fun['script'] == '__init__.py':
                    research_func = reverse_fun
                    logging.info(f"Found research_func: {research_func}")
            if self.slice_end < total_items:
                self.console.print(f"\n[green]Press [red]Enter [green]for next page, [red]'q' [green]to quit, [red]'back' [green]to search, [red]'next' [green]for next manager, or [red]'prev' [green]for previous manager.")
                if not force_int_input:
                    key = Prompt.ask(
                        "\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                        "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end"
                    )
                else:
                    choices = [str(i) for i in range(0, max_int_input)]
                    choices.extend(["q", "", "back", "next", "prev"])
                    key = Prompt.ask("[cyan]Insert media [red]index", choices=choices, show_choices=False)
                last_command = key
                if key.lower() == "q":
                    return "quit"
                elif key == "":
                    self.slice_start += self.step
                    self.slice_end += self.step
                    if self.slice_end > total_items:
                        self.slice_end = total_items
                elif key.lower() == "back" and research_func:
                    self.run_back_command(research_func)
                elif key.lower() == "next":
                    return "next"
                elif key.lower() == "prev":
                    return "prev"
                else:
                    break
            else:
                self.console.print(f"\n [green]You've reached the end. [red]Enter [green]for first page, [red]'q' [green]to quit, [red]'back' [green]to search, [red]'next' [green]for next manager, or [red]'prev' [green]for previous manager.")
                if not force_int_input:
                    key = Prompt.ask(
                        "\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                        "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end"
                    )
                else:
                    choices = [str(i) for i in range(0, max_int_input)]
                    choices.extend(["q", "", "back", "next", "prev"])
                    key = Prompt.ask("[cyan]Insert media [red]index", choices=choices, show_choices=False)
                last_command = key
                if key.lower() == "q":
                    return "quit"
                elif key == "":
                    self.slice_start = 0
                    self.slice_end = self.step
                elif key.lower() == "back" and research_func:
                    self.run_back_command(research_func)
                elif key.lower() == "next":
                    return "next"
                elif key.lower() == "prev":
                    return "prev"
                else:
                    break
        return last_command
    '''

    def run(self, force_int_input: bool = False, max_int_input: int = 0) -> str:
        total_items = len(self.tv_shows)
        last_command = ""
        while True:
            start_message()
            self.display_data(self.tv_shows[self.slice_start:self.slice_end])
            research_func = None
            for reverse_fun in get_call_stack():
                if reverse_fun['function'] == 'search' and reverse_fun['script'] == '__init__.py':
                    research_func = reverse_fun
                    logging.info(f"Found research_func: {research_func}")

            if self.slice_end < total_items:
                # Display different options based on whether it's a global search or not
                if self.isGlobal:
                    self.console.print(
                        f"\n[green]Press [red]Enter [green]for next page, [red]'q' [green]to quit, [red]'back' [green]to search, [red]'next' [green]for next provider, or [red]'prev' [green]for previous provider.")
                else:
                    self.console.print(
                        f"\n[green]Press [red]Enter [green]for next page, [red]'q' [green]to quit, or [red]'back' [green]to search.")

                if not force_int_input:
                    key = Prompt.ask(
                        "\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                        "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end"
                    )
                else:
                    choices = [str(i) for i in range(0, max_int_input)]
                    if self.isGlobal:
                        choices.extend(["q", "", "back", "next", "prev"])
                    else:
                        choices.extend(["q", "", "back"])
                    key = Prompt.ask("[cyan]Insert media [red]index", choices=choices, show_choices=False)

                last_command = key
                if key.lower() == "q":
                    return "quit"
                elif key == "":
                    self.slice_start += self.step
                    self.slice_end += self.step
                    if self.slice_end > total_items:
                        self.slice_end = total_items
                elif key.lower() == "back" and research_func:
                    self.run_back_command(research_func)
                elif key.lower() == "next" and self.isGlobal:
                    return "next"
                elif key.lower() == "prev" and self.isGlobal:
                    return "prev"
                else:
                    break
            else:
                # Display different options based on whether it's a global search or not
                if self.isGlobal:
                    self.console.print(
                        f"\n [green]You've reached the end. [red]Enter [green]for first page, [red]'q' [green]to quit, [red]'back' [green]to search, [red]'next' [green]for next manager, or [red]'prev' [green]for previous manager.")
                else:
                    self.console.print(
                        f"\n [green]You've reached the end. [red]Enter [green]for first page, [red]'q' [green]to quit, or [red]'back' [green]to search.")

                if not force_int_input:
                    key = Prompt.ask(
                        "\n[cyan]Insert media index [yellow](e.g., 1), [red]* [cyan]to download all media, "
                        "[yellow](e.g., 1-2) [cyan]for a range of media, or [yellow](e.g., 3-*) [cyan]to download from a specific index to the end"
                    )
                else:
                    choices = [str(i) for i in range(0, max_int_input)]
                    if self.isGlobal:
                        choices.extend(["q", "", "back", "next", "prev"])
                    else:
                        choices.extend(["q", "", "back"])
                    key = Prompt.ask("[cyan]Insert media [red]index", choices=choices, show_choices=False)

                last_command = key
                if key.lower() == "q":
                    return "quit"
                elif key == "":
                    self.slice_start = 0
                    self.slice_end = self.step
                elif key.lower() == "back" and research_func:
                    self.run_back_command(research_func)
                elif key.lower() == "next" and self.isGlobal:
                    return "next"
                elif key.lower() == "prev" and self.isGlobal:
                    return "prev"
                else:
                    break
        return last_command

    def clear(self):
        self.tv_shows = []