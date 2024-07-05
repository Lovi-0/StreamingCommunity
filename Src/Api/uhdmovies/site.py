# 09.06.24

import logging


# External libraries
import httpx
from bs4 import BeautifulSoup
from unidecode import unidecode


# Internal utilities
from Src.Util.table import TVShowManager
from ..Template import search_domain, get_select_title


# Logic class
from .Core.Class.SearchType import MediaManager


# Variable
from .costant import SITE_NAME
media_search_manager = MediaManager()
table_show_manager = TVShowManager()



def title_search(word_to_search: str) -> int:
    """
    Search for titles based on a search query.

    Args:
        - title_search (str): The title to search for.

    Returns:
        int: The number of titles found.
    """

    # Create a web automation driver instance
    domain_to_use, _ = search_domain(SITE_NAME, '<meta name="description" content="Download 1080p', f"https://{SITE_NAME}")

    # Construct the full site URL and load the search page
    response = httpx.get(f"https://{SITE_NAME}.{domain_to_use}/search/{unidecode(word_to_search)}")
    response.raise_for_status()

    # Retrieve and parse the HTML content of the page
    soup = BeautifulSoup(response.text, "html.parser")
    table_content = soup.find_all("article")

    # Iterate through the search results to find relevant titles
    for title in table_content:
            
        # Construct a media object with the title's details
        obj = {
            'url':  title.find("a").get("href"),
            'name': title.find("a").get("title"),
        }

        # Add the media object to the media search manager
        media_search_manager.add_media(obj)
    
    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager) 