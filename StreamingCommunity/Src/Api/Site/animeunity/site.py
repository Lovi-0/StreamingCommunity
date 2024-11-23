# 10.12.23

import logging


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from StreamingCommunity.Src.Util.console import console
from StreamingCommunity.Src.Util._jsonConfig import config_manager
from StreamingCommunity.Src.Util.table import TVShowManager


# Logic class
from StreamingCommunity.Src.Api.Template import get_select_title
from StreamingCommunity.Src.Api.Template.Util import search_domain
from StreamingCommunity.Src.Api.Template.Class.SearchType import MediaManager


# Variable
from .costant import SITE_NAME
media_search_manager = MediaManager()
table_show_manager = TVShowManager()



def get_token(site_name: str, domain: str) -> dict:
    """
    Function to retrieve session tokens from a specified website.

    Parameters:
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


def get_real_title(record):
    """
    Get the real title from a record.

    This function takes a record, which is assumed to be a dictionary representing a row of JSON data.
    It looks for a title in the record, prioritizing English over Italian titles if available.
    
    Parameters:
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

    Parameters:
        - title_search (str): The title to search for.

    Returns:
        - int: A number containing the length of media search manager.
    """

    # Get token and session value from configuration
    max_timeout = config_manager.get_int("REQUESTS", "timeout")
    domain_to_use, _ = search_domain(SITE_NAME, f"https://www.{SITE_NAME}")
    
    data = get_token(SITE_NAME, domain_to_use)

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
        'title': title  # Use the provided title for the search
    }

    # Send a POST request to the API endpoint for live search
    try:
        response = httpx.post(
            url=f'https://www.{SITE_NAME}.{domain_to_use}/livesearch', 
            cookies=cookies, 
            headers=headers, 
            json=json_data,
            timeout=max_timeout
        )
        response.raise_for_status()

    except Exception as e:
        console.print(f"Site: {SITE_NAME}, request search error: {e}")

    # Process each record returned in the response
    for dict_title in response.json()['records']:

        # Rename keys for consistency
        dict_title['name'] = get_real_title(dict_title)

        # Add the record to media search manager if the name is not None
        media_search_manager.add_media({
            'id': dict_title.get('id'),
            'slug': dict_title.get('slug'),
            'name': dict_title.get('name'),
            'type': dict_title.get('type'),
            'score': dict_title.get('score'),
            'episodes_count': dict_title.get('episodes_count')
        })

    # Return the length of media search manager
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)