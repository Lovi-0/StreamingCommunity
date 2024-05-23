# 08.05.24

import logging


# Internal utilities
from Src.Api.Streamingcommunity import (
    get_version_and_domain,
    title_search,
    manager_clear,
    get_select_title
)

from Src.Util.message import start_message
from Src.Util._jsonConfig import config_manager
from Src.Util.console import console, msg
from Src.Lib.E_Table import job_database
from Src.Api.Streamingcommunity.Core.Vix_player.player import VideoSource


# Config
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
SERIES_FOLDER = config_manager.get('DEFAULT', 'series_folder_name')
STREAM_SITE_NAME = config_manager.get('SITE', 'streaming_site_name')
DOMAIN_SITE_NAME = config_manager.get('SITE', 'streaming_domain')
CREATE_JOB_DB = config_manager.get_bool('DEFAULT', 'create_job_database')


class SuppressedConsolePrint:
    def __enter__(self):
        self.original_print = console.print
        console.print = lambda *args, **kwargs: None
    
    def __exit__(self, exc_type, exc_value, traceback):
        console.print = self.original_print


class SeriesManager:
    def __init__(self):
        """
        Initialize SeriesManager object.
        """
        with SuppressedConsolePrint():
            self.version, self.domain = get_version_and_domain()
            self.video_source = VideoSource()

    def add_series(self):
        """
        Add a new series to the database.
        """
        try:

            # Ask the user to input the search term
            input_title_search = msg.ask("\n[cyan]Insert word to search in all site: [/cyan]")

            if input_title_search:

                # Perform streaming search based on the search term
                len_database = title_search(input_title_search, self.domain)

                if len_database != 0:

                    # Get the selected title from the search results
                    select_title = get_select_title(type_filter=['tv'])

                    if select_title.type == 'tv':

                        # Set series name and media ID for the selected title
                        self.video_source.setup(
                            domain = DOMAIN_SITE_NAME,
                            series_name = select_title.slug,
                            media_id = select_title.id
                        )

                        # Collect info about the season
                        self.video_source.get_preview()
                        seasons_count = self.video_source.obj_preview.seasons_count

                        # Add the series to the database
                        console.print("[green]Series '[/green][bold cyan]" + select_title.slug + "[/bold cyan][green]' added successfully.[/green]")
                        job_database.add_row_to_database(select_title.id, select_title.slug, seasons_count)
                        job_database.save_database()

                        # Clear old data added
                        manager_clear()
                        
                else:
                    console.print("[red]No series found for the given search term.[/red]")
            else:
                console.print("[red]Invalid choice. Please select a valid option.[/red]")

        except Exception as e:
            logging.error(f"Error occurred while adding series: {str(e)}")

    def check_series(self):
        """
        Check for new seasons in existing series.
        """
        try:
            
            # Loop through each series in the database
            for data_series in job_database.db[1:]:
                self.video_source.setup(
                    domain = DOMAIN_SITE_NAME,
                    series_name = data_series[1],
                    media_id = data_series[0]
                )

                # Collect information about seasons for the series
                self.video_source.get_preview()
                seasons_count = self.video_source.obj_preview.seasons_count
                
                if int(data_series[2]) < seasons_count:

                    # Notify if a new season is found for the series
                    console.print("[bold yellow]Series '[/bold yellow][bold cyan]" + data_series[1] + "[/bold cyan][bold yellow]' found new season.[/bold yellow]")
                else:

                    # Notify if no new seasons are found for the series
                    console.print("[bold red]Series '[/bold red][bold cyan]" + data_series[1] + "[/bold cyan][bold red]' has no new seasons.[/bold red]")

        except Exception as e:
            logging.error(f"Error occurred while checking series: {str(e)}")

    def list_series(self):
        """
        Print the list of series in the database.
        """
        try:

            # Print the header for the series list
            console.print("\n[bold cyan]Series List:[/bold cyan]\n")
            job_database.print_database_as_sql()

        except Exception as e:
            logging.error(f"Error occurred while listing series: {str(e)}")

    def remove_series(self):
        """
        Remove a series from the database.
        """

        if len(job_database.db) > 1:

                # Ask the user to input the index of the series to remove
                index_to_remove = msg.ask("\n[cyan]Insert [bold red]ID [cyan]to remove").strip()

                if index_to_remove != 0:

                    # Remove the series from the database
                    data_row_remove = job_database.remove_row_from_database(0, index_to_remove)
                    job_database.save_database()

                    if data_row_remove:
                        console.print("[bold green]Series '[/bold green][bold cyan]" + data_row_remove[1] + "[/bold cyan][bold green]' removed successfully.[/bold green]")

                else:
                    console.print("[bold red]Cannot remove columns from the database.[/bold red]")

        else:
            console.print("[bold yellow]No data to remove[/bold yellow]")

    def run(self):
        """
        Run the SeriesManager application.
        """
        while True:

            # Reload all database all time
            start_message()
            job_database.load_database()

            # Prompt the user for action choice
            action = msg.ask("\n[green]What would you like to do?", choices=["add", "check", "remove", "print", "quit"])

            if action == "add":
                self.add_series()
            elif action == "check":
                self.check_series()
            elif action == "remove":
                self.remove_series()
            elif action == "print":
                self.list_series()
            elif action == "quit":
                console.print("\n[bold magenta]Exiting Series Manager. Goodbye![/bold magenta]")
                break
            else:
                console.print("[red]Invalid action. Please try again.[/red]")

            confirmation = msg.ask("\n[blue]Press 'y' to continue, or 'n' to quit[/blue]")
            if confirmation.lower() == "n":
                console.print("\n[bold magenta]Exiting Series Manager. Goodbye![/bold magenta]")
                break


def main():

    if CREATE_JOB_DB:
        manager = SeriesManager()
        manager.run()
    else:
        console.print("[red]Set to true 'create_job_database' on config.json file.")

if __name__ == '__main__':
    main()