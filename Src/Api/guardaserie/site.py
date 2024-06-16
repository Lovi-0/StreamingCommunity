# 09.06.24

import sys
import logging


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.table import TVShowManager
from Src.Util.console import console, msg
from Src.Util.headers import get_headers


# Logic class
from .Core.Class.SearchType import MediaManager, MediaItem


# Variable
from .costant import DOMAIN_NOW
media_search_manager = MediaManager()
table_show_manager = TVShowManager()


def title_search(word_to_search) -> int:
    """
    Search for titles based on a search query.
    """

    # Send request to search for titles
    response = httpx.get(f"https://guardaserie.{DOMAIN_NOW}/?story={word_to_search}&do=search&subaction=search", headers={'user-agent': get_headers()})
    response.raise_for_status()

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")
    table_content = soup.find('div', class_="mlnew-list")

    for serie_div in table_content.find_all('div', class_='mlnew'):

        try:
            title = serie_div.find('div', class_='mlnh-2').find("h2").get_text(strip=True)
            link = serie_div.find('div', class_='mlnh-2').find('a')['href']
            imdb_rating = serie_div.find('span', class_='mlnh-imdb').get_text(strip=True)

            serie_info = {
                'name': title,
                'url': link,
                'score': imdb_rating
            }

            media_search_manager.add_media(serie_info)

        except:
            pass

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
