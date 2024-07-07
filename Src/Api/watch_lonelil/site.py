# 09.06.24

import logging


# External libraries
from unidecode import unidecode


# Internal utilities
from Src.Util.table import TVShowManager
from Src.Lib.Driver import WebAutomation
from ..Template import search_domain, get_select_title


# Logic class
from ..Template.Class.SearchType import MediaManager


# Variable
from .costant import SITE_NAME, DOMAIN_NOW
media_search_manager = MediaManager()
table_show_manager = TVShowManager()


def title_search(word_to_search: str) -> int:
    """
    Search for titles based on a search query.

    Parameters:
        - title_search (str): The title to search for.

    Returns:
        int: The number of titles found.
    """

    # Create a web automation driver instance
    main_driver = WebAutomation()

    # Construct the full site URL and load the search page
    full_site_name = f"{SITE_NAME}.{DOMAIN_NOW}"
    main_driver.get_page(f"https://{full_site_name}/search?q={unidecode(word_to_search)}")

    # Retrieve and parse the HTML content of the page
    soup = main_driver.retrieve_soup()
    content_table = soup.find_all("a")

    # Iterate through the search results to find relevant titles
    for title in content_table:
        if any(keyword in str(title).lower() for keyword in ["show/", "movie/", "anime/"]):
            
            obj = {
                'url': f"https://{full_site_name}" + title.get("href"),
                'name': title.find("img").get("alt"),
                'type': title.find_all("p")[-1].get_text().split("·")[0].strip().lower()
            }

            media_search_manager.add_media(obj)
    
    # Return the number of titles found
    return media_search_manager.get_length(), main_driver


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager) 