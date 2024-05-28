# 10.12.23

import sys
import json
import logging

from typing import Tuple


# External libraries
from bs4 import BeautifulSoup
from unidecode import unidecode


# Internal utilities
from Src.Util.table import TVShowManager
from Src.Lib.Request import requests
from Src.Util.headers import get_headers
from Src.Util.console import console
from Src.Util._jsonConfig import config_manager


# Logic class
from .Core.Util import extract_domain
from .Core.Class.SearchType import MediaManager, MediaItem


# Config
SC_SITE_NAME = "streamingcommunity"
SC_DOMAIN_NOW = config_manager.get('SITE', SC_SITE_NAME)


# Variable
media_search_manager = MediaManager()
table_show_manager = TVShowManager()



def get_version(text: str) -> tuple[str, list]:
    """
    Extracts the version from the HTML text of a webpage.

    Args:
        - text (str): The HTML text of the webpage.

    Returns:
        str: The version extracted from the webpage.
        list: Top 10 titles headlines for today.
    """
    console.print("[cyan]Make request to get version [white]...")

    try:

        # Parse request to site
        soup = BeautifulSoup(text, "html.parser")

        # Extract version
        version = json.loads(soup.find("div", {"id": "app"}).get("data-page"))['version']
        sliders = json.loads(soup.find("div", {"id": "app"}).get("data-page"))['props']['sliders']

        title_top_10 = sliders[2]

        # Collect info about only top 10 title
        list_title_top_10 = []
        for title in title_top_10['titles']:
            list_title_top_10.append({
                'name': title['name'],
                'type': title['type']
            })

        console.print(f"[cyan]Get version [white]=> [red]{version} \n")

        return version, list_title_top_10
    
    except Exception as e:
        logging.error(f"Error extracting version: {e}")
        raise


def get_version_and_domain(new_domain = None) -> Tuple[str, str]:
    """
    Retrieves the version and domain of the streaming website.

    This function retrieves the version and domain of the streaming website.
    It first checks the accessibility of the current site.
    If the site is accessible, it extracts the version from the response.
    If configured to do so, it also scrapes and prints the titles of the moments.
    If the site is inaccessible, it attempts to obtain a new domain using the 'insta' method.

    Returns:
        Tuple[str, str]: A tuple containing the version and domain.
    """
    
    # Get the current domain from the configuration
    if new_domain is None:
        config_domain = config_manager.get('SITE', SC_SITE_NAME)
    else:
        config_domain = new_domain

    # Test the accessibility of the current site
    try:

        # Make requests to site to get text
        console.print(f"[cyan]Test site[white]: [red]https://{SC_SITE_NAME}.{config_domain}")
        response = requests.get(f"https://{SC_SITE_NAME}.{config_domain}")
        console.print(f"[cyan]Test respost site[white]: [red]{response.status_code} \n")

        # Extract version from the response
        version, list_title_top_10 = get_version(response.text)

        return version, config_domain

    except:

        console.print("[red]\nExtract new DOMAIN from TLD list.")
        new_domain = extract_domain(method="light")
        console.log(f"[cyan]Extract new domain: [red]{new_domain}")

        # Update the domain in the configuration file
        config_manager.set_key('SITE', SC_SITE_NAME, str(new_domain))
        config_manager.write_config()

        # Retry to get the version and domain
        return get_version_and_domain(new_domain)


def title_search(title_search: str, domain: str) -> int:
    """
    Search for titles based on a search query.

    Args:
        - title_search (str): The title to search for.
        - domain (str): The domain to search on.

    Returns:
        int: The number of titles found.
    """
    
    # Send request to search for titles ( replace à to a and space to "+" )
    response = requests.get(f"https://{SC_SITE_NAME}.{domain}/api/search?q={unidecode(title_search.replace(' ', '+'))}", headers={'user-agent': get_headers()})

    # Add found titles to media search manager
    for dict_title in response.json()['data']:
        media_search_manager.add_media(dict_title)

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
        "Date": {'color': 'green'}
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
            'Date': media.last_air_date
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
