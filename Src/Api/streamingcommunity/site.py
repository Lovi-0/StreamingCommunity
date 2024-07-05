# 10.12.23

import sys
import json
import logging


# External libraries
import httpx
from bs4 import BeautifulSoup
from unidecode import unidecode


# Internal utilities
from Src.Util.headers import get_headers
from Src.Util.console import console
from Src.Util.table import TVShowManager
from ..Template import search_domain, get_select_title


# Logic class
from .Core.Class.SearchType import MediaManager


# Config
from .costant import SITE_NAME


# Variable
media_search_manager = MediaManager()
table_show_manager = TVShowManager()



def get_version(text: str):
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


def get_version_and_domain():
    """
    Retrieve the current version and domain of the site.

    This function performs the following steps:
        - Determines the correct domain to use for the site by searching for a specific meta tag.
        - Fetches the content of the site to extract the version information.
    """

    # Find new domain if prev dont work
    domain_to_use, base_url = search_domain(SITE_NAME, '<meta name="author" content="StreamingCommunity">', f"https://{SITE_NAME}")

    # Extract version from the response
    version, list_title_top_10 = get_version(httpx.get(base_url, headers={'user-agent': get_headers()}).text)

    return version, domain_to_use


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
    response = httpx.get(f"https://{SITE_NAME}.{domain}/api/search?q={unidecode(title_search.replace(' ', '+'))}", headers={'user-agent': get_headers()})
    response.raise_for_status()

    # Add found titles to media search manager
    for dict_title in response.json()['data']:
        media_search_manager.add_media(dict_title)

    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)