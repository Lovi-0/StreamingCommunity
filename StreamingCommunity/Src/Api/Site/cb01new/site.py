# 03.07.24

# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from StreamingCommunity.Src.Util._jsonConfig import config_manager
from StreamingCommunity.Src.Util.headers import get_headers
from StreamingCommunity.Src.Util.table import TVShowManager


# Logic class
from StreamingCommunity.Src.Api.Template import get_select_title
from StreamingCommunity.Src.Api.Template.Util import search_domain
from StreamingCommunity.Src.Api.Template.Class.SearchType import MediaManager


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
    max_timeout = config_manager.get_int("REQUESTS", "timeout")
    domain_to_use, _ = search_domain(SITE_NAME, f"https://{SITE_NAME}")

    response = httpx.get(
        url=f"https://{SITE_NAME}.{domain_to_use}/?s={word_to_search}",
        headers={'user-agent': get_headers()},
        timeout=max_timeout
    )
    response.raise_for_status()

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")

    # For all element in table
    for div in soup.find_all("div", class_ = "card-content"):

        url = div.find("h3").find("a").get("href")
        title = div.find("h3").find("a").get_text(strip=True)
        desc = div.find("p").find("strong").text

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
