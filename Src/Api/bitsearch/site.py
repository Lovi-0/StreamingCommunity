# 01.07.24

import sys
import logging


# External libraries
import httpx
from bs4 import BeautifulSoup
from unidecode import unidecode


# Internal utilities
from Src.Util.headers import get_headers
from Src.Util.table import TVShowManager
from ..Template import search_domain, get_select_title


# Logic class
from ..Template.Class.SearchType import MediaManager


# Variable
from .costant import SITE_NAME
media_search_manager = MediaManager()
table_show_manager = TVShowManager()



def title_search(word_to_search: str) -> int:
    """
    Search for titles based on a search query.
    
    Parameters:
        - title_search (str): The title to search for.

    Returns:
        - int: The number of titles found.
    """

    # Find new domain if prev dont work
    domain_to_use, _ = search_domain(SITE_NAME, '<meta name="description" content="Bitsearch is #1 Torrent Index ever.">g', f"https://{SITE_NAME}")

    # Construct the full site URL and load the search page
    response = httpx.get(f"https://{SITE_NAME}.{domain_to_use}/search?q={unidecode(word_to_search)}&category=1&subcat=2&page=1", headers={'user-agent': get_headers()})
    response.raise_for_status()

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")

    for title_div in soup.find_all("li", class_ = "card"):

        title_info = {
            'name': title_div.find("a").get_text(strip=True),
            'url': title_div.find_all("a")[-1].get("href"),
            'size': title_div.find_all("div")[-5].get_text(strip=True),
            'seader': title_div.find_all("div")[-4].get_text(strip=True),
            'leacher': title_div.find_all("div")[-3].get_text(strip=True),
            'date': title_div.find_all("div")[-2].get_text(strip=True)
        }

        media_search_manager.add_media(title_info)

    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager) 