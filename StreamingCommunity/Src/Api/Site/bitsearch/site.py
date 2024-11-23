# 01.07.24

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
            url=f"https://{SITE_NAME}.{domain_to_use}/search?q={word_to_search}&category=1&subcat=2&page=1", 
            headers={'user-agent': get_headers()}, 
            timeout=max_timeout
        )
        response.raise_for_status()

    except Exception as e:
        console.print(f"Site: {SITE_NAME}, request search error: {e}")

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")

    for title_div in soup.find_all("li", class_ = "card"):
        try:
            div_stats = title_div.find("div", class_ = "stats")

            title_info = {
                'name': title_div.find("a").get_text(strip=True),
                'url': title_div.find_all("a")[-1].get("href"),
                #'nDownload': div_stats.find_all("div")[0].get_text(strip=True),
                'size': div_stats.find_all("div")[1].get_text(strip=True),
                'seader': div_stats.find_all("div")[2].get_text(strip=True),
                'leacher': div_stats.find_all("div")[3].get_text(strip=True),
                'date': div_stats.find_all("div")[4].get_text(strip=True)
            }

            media_search_manager.add_media(title_info)
            
        except:
            pass

    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager) 
