# 02.07.24

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

    # Construct the full site URL and load the search page
    try:
        response = httpx.get(
            url=f"https://{SITE_NAME}.{domain_to_use}/search/{word_to_search}/1/", 
            headers={'user-agent': get_headers()}, 
            follow_redirects=True,
            timeout=max_timeout
        )
        response.raise_for_status()

    except Exception as e:
        console.print(f"Site: {SITE_NAME}, request search error: {e}")

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")

    # Scrape div film in table on single page
    for tr in soup.find_all('tr'):
        try:

            title_info = {
                'name': tr.find_all("a")[1].get_text(strip=True),
                'url': tr.find_all("a")[1].get("href"),
                'seader': tr.find_all("td")[-5].get_text(strip=True),
                'leacher': tr.find_all("td")[-4].get_text(strip=True),
                'date': tr.find_all("td")[-3].get_text(strip=True).replace("'", ""),
                'size': tr.find_all("td")[-2].get_text(strip=True)
            }
            
            media_search_manager.add_media(title_info)

        except:
            continue

    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)