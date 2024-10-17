# 03.07.24

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
    domain_to_use, _ = search_domain(SITE_NAME, f"https://{SITE_NAME}")

    # Send request to search for titles
    response = httpx.get(f"https://{SITE_NAME}.{domain_to_use}/?s={unidecode(word_to_search)}", headers={'user-agent': get_headers()}, follow_redirects=True)
    response.raise_for_status()

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")

    for div_title in soup.find_all("div", class_ = "card"):

        url = div_title.find("h3").find("a").get("href")
        title = div_title.find("h3").find("a").get_text(strip=True)
        desc = div_title.find("p").find("strong").text

        title_info = {
            'name': title,
            'desc': desc,
            'url': url
        }

        media_search_manager.add_media(title_info)

    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)
