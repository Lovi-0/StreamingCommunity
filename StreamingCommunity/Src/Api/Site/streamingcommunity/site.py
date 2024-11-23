# 10.12.23

import sys
import json
import logging


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from StreamingCommunity.Src.Util.console import console
from StreamingCommunity.Src.Util._jsonConfig import config_manager
from StreamingCommunity.Src.Util.headers import get_headers
from StreamingCommunity.Src.Util.table import TVShowManager



# Logic class
from StreamingCommunity.Src.Api.Template import get_select_title
from StreamingCommunity.Src.Api.Template.Util import search_domain
from StreamingCommunity.Src.Api.Template.Class.SearchType import MediaManager


# Config
from .costant import SITE_NAME


# Variable
media_search_manager = MediaManager()
table_show_manager = TVShowManager()



def get_version(text: str):
    """
    Extracts the version from the HTML text of a webpage.

    Parameters:
        - text (str): The HTML text of the webpage.

    Returns:
        str: The version extracted from the webpage.
        list: Top 10 titles headlines for today.
    """
    try:

        # Parse request to site
        soup = BeautifulSoup(text, "html.parser")

        # Extract version
        version = json.loads(soup.find("div", {"id": "app"}).get("data-page"))['version']
        #console.print(f"[cyan]Get version [white]=> [red]{version} \n")

        return version
    
    except Exception as e:
        logging.error(f"Error extracting version: {e}")
        raise


def get_version_and_domain():
    """
    Retrieve the current version and domain of the site.

    This function performs the following steps:
        - Determines the correct domain to use for the site by searching for a specific meta tag.
        - Fetches the content of the site to extract the version information.
    """

    # Find new domain if prev dont work
    domain_to_use, base_url = search_domain(SITE_NAME, f"https://{SITE_NAME}")

    # Extract version from the response
    version = get_version(httpx.get(base_url, headers={'user-agent': get_headers()}).text)

    return version, domain_to_use


def title_search(title_search: str, domain: str) -> int:
    """
    Search for titles based on a search query.

    Parameters:
        - title_search (str): The title to search for.
        - domain (str): The domain to search on.

    Returns:
        int: The number of titles found.
    """

    max_timeout = config_manager.get_int("REQUESTS", "timeout")
    
    # Send request to search for titles ( replace à to a and space to "+" )
    try:
        response = httpx.get(
            url=f"https://{SITE_NAME}.{domain}/api/search?q={title_search.replace(' ', '+')}", 
            headers={'user-agent': get_headers()}, 
            timeout=max_timeout
        )
        response.raise_for_status()

    except Exception as e:
        console.print(f"Site: {SITE_NAME}, request search error: {e}")

    # Add found titles to media search manager
    for dict_title in response.json()['data']:
        media_search_manager.add_media({
            'id': dict_title.get('id'),
            'slug': dict_title.get('slug'),
            'name': dict_title.get('name'),
            'type': dict_title.get('type'),
            'score': dict_title.get('score')
        })

    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)