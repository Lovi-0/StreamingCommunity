# 26.05.24

import sys
import json
import logging


# External libraries
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.table import TVShowManager
from Src.Lib.Request import requests
from Src.Util.headers import get_headers
from Src.Util.console import console
from Src.Util._jsonConfig import config_manager

# Logic class
from .Core.Class.SearchType import MediaManager, MediaItem


# Config
AD_SITE_NAME = "altadefinizione"
AD_DOMAIN_NOW = config_manager.get('SITE', AD_SITE_NAME)


# Variable
media_search_manager = MediaManager()
table_show_manager = TVShowManager()



def title_search(title_search: str) -> int:
    """
    Search for titles based on a search query.

    Args:
        - title_search (str): The title to search for.
        - domain (str): The domain to search on.

    Returns:
        int: The number of titles found.
    """
    
    # Send request to search for titles
    response = requests.get(f"https://{AD_SITE_NAME}.{AD_DOMAIN_NOW}/page/1/?story={title_search.replace(' ', '+')}&do=search&subaction=search&titleonly=3")

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")
    table_content = soup.find('div', id="dle-content")

    # Scrape div film in table on single page
    for film_div in table_content.find_all('div', class_='col-lg-3'):
        title = film_div.find('h2', class_='titleFilm').get_text(strip=True)
        link = film_div.find('h2', class_='titleFilm').find('a')['href']
        imdb_rating = film_div.find('div', class_='imdb-rate').get_text(strip=True).split(":")[-1]

        film_info = {
            'name': title,
            'url': link,
            'score': imdb_rating
        }

        media_search_manager.add_media(film_info)

    # Return the number of titles found
    return media_search_manager.get_length()


def get_select_title(type_filter: list = None) -> MediaItem:
    """
    Display a selection of titles and prompt the user to choose one.

    Args:
        - type_filter (list): A list of media types to filter. Can include 'film', 'tv', 'ova'. Ex. ['tv', 'film']

    Returns:
        MediaItem: The selected media item.
    """

    # Set up table for displaying titles
    table_show_manager.set_slice_end(10)

    # Add columns to the table
    column_info = {
        "Index": {'color': 'red'},
        "Name": {'color': 'magenta'},
        "Type": {'color': 'yellow'},
        "Score": {'color': 'cyan'},
    }
    table_show_manager.add_column(column_info)

    # Populate the table with title information
    for i, media in enumerate(media_search_manager.media_list):
        
        # Filter for only a list of category
        if type_filter is not None:
            if str(media.type) not in type_filter:
                continue
            
        table_show_manager.add_tv_show({
            'Index': str(i),
            'Name': media.name,
            'Type': media.type,
            'Score': media.score,
        })

    # Run the table and handle user input
    last_command = table_show_manager.run(force_int_input=True, max_int_input=len(media_search_manager.media_list))
    table_show_manager.clear()

    # Handle user's quit command
    if last_command == "q":
        console.print("\n[red]Quit [white]...")
        sys.exit(0)

    # Check if the selected index is within range
    if 0 <= int(last_command) <= len(media_search_manager.media_list):
        return media_search_manager.get(int(last_command))
    else:
        console.print("\n[red]Wrong index")
        sys.exit(0)


def manager_clear():
    """
    Clears the data lists managed by media_search_manager and table_show_manager.

    This function clears the data lists managed by global variables media_search_manager
    and table_show_manager. It removes all the items from these lists, effectively
    resetting them to empty lists.
    """
    global media_search_manager, table_show_manager

    # Clear list of data
    media_search_manager.clear()
    table_show_manager.clear()
