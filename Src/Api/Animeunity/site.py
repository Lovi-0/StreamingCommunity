# 10.12.23

import sys
import logging


# External libraries
import httpx
from bs4 import BeautifulSoup
from unidecode import unidecode


# Internal utilities
from Src.Util.table import TVShowManager
from Src.Util.console import console
from Src.Util._jsonConfig import config_manager


# Logic class
from .Core.Util import extract_domain
from .Core.Class.SearchType import MediaManager, MediaItem


# Config
SITE_NAME = "animeunity"
DOMAIN_NOW = config_manager.get('SITE', SITE_NAME)


# Variable
media_search_manager = MediaManager()
table_show_manager = TVShowManager()



def get_token(site_name: str, domain: str) -> dict:
    """
    Function to retrieve session tokens from a specified website.

    Args:
        - site_name (str): The name of the site.
        - domain (str): The domain of the site.

    Returns:
        - dict: A dictionary containing session tokens. The keys are 'XSRF_TOKEN', 'animeunity_session', and 'csrf_token'.
    """

    # Send a GET request to the specified URL composed of the site name and domain
    response = httpx.get(f"https://www.{site_name}.{domain}")
    response.raise_for_status()

    # Initialize variables to store CSRF token
    find_csrf_token = None
    
    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Loop through all meta tags in the HTML response
    for html_meta in soup.find_all("meta"):

        # Check if the meta tag has a 'name' attribute equal to "csrf-token"
        if html_meta.get('name') == "csrf-token":

            # If found, retrieve the content of the meta tag, which is the CSRF token
            find_csrf_token = html_meta.get('content')

    logging.info(f"Extract: ('animeunity_session': {response.cookies['animeunity_session']}, 'csrf_token': {find_csrf_token})")
    return {
        'animeunity_session': response.cookies['animeunity_session'],
        'csrf_token': find_csrf_token
    }


def update_domain():
    """
    Update the domain for the anime streaming site.

    This function tests the accessibility of the current anime streaming site.
    If the current domain is inaccessible, it attempts to obtain and set a new domain.
    It uses the 'light' method to extract a new domain from Anime Unity.
    """

    # Test current site's accessibility
    try:
        
        console.log(f"[cyan]Test site: [red]https://{SITE_NAME}.{DOMAIN_NOW}")
        response = httpx.get(f"https://www.{SITE_NAME}.{DOMAIN_NOW}")
        response.status_code

    # If the current site is inaccessible, try to obtain a new domain
    except Exception as e:

        # Get new domain
        console.print("[red]\nExtract new DOMAIN from TLD list.")
        new_domain = extract_domain(method="light")
        console.log(f"[cyan]Extract new domain: [red]{new_domain}")

        if new_domain:

            # Update configuration with the new domain
            config_manager.set_key('SITE', SITE_NAME, new_domain)
            config_manager.write_config()

        else:
            logging.error("Failed to find a new animeunity domain")
            sys.exit(0)


def get_real_title(record):
    """
    Get the real title from a record.

    This function takes a record, which is assumed to be a dictionary representing a row of JSON data.
    It looks for a title in the record, prioritizing English over Italian titles if available.
    
    Args:
        - record (dict): A dictionary representing a row of JSON data.
    
    Returns:
        - str: The title found in the record. If no title is found, returns None.
    """

    if record['title'] is not None:
        return record['title']
    
    elif record['title_eng'] is not None:
        return record['title_eng']
    
    else:
        return record['title_it']


def title_search(title: str) -> int:
    """
    Function to perform an anime search using a provided title.

    Args:
        - title_search (str): The title to search for.

    Returns:
        - int: A number containing the length of media search manager.
    """

    # Update domain
    update_domain()

    # Get token and session value from configuration
    url_domain = config_manager.get('SITE', SITE_NAME)  
    data = get_token(SITE_NAME, url_domain)

    # Prepare cookies to be used in the request
    cookies = {
        'animeunity_session': data.get('animeunity_session')
    }

    # Prepare headers for the request
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json;charset=UTF-8',
        'x-csrf-token': data.get('csrf_token')
    }

    # Prepare JSON data to be sent in the request
    json_data = {
        'title': unidecode(title)  # Use the provided title for the search
    }

    # Send a POST request to the API endpoint for live search
    response = httpx.post(f'https://www.{SITE_NAME}.{url_domain}/livesearch', cookies=cookies, headers=headers, json=json_data)
    response.raise_for_status()

    # Process each record returned in the response
    for record in response.json()['records']:

        # Rename keys for consistency
        record['name'] = get_real_title(record)
        record['last_air_date'] = record.pop('date')  

        # Add the record to media search manager if the name is not None
        media_search_manager.add_media(record)

    # Return the length of media search manager
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

