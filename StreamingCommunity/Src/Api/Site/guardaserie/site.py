# 09.06.24

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

    # Send request to search for titles
    try:
        response = httpx.get(
            url=f"https://guardaserie.{domain_to_use}/?story={word_to_search}&do=search&subaction=search", 
            headers={'user-agent': get_headers()}, 
            timeout=max_timeout
        )
        response.raise_for_status()
    
    except Exception as e:
        console.print(f"Site: {SITE_NAME}, request search error: {e}")

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")
    table_content = soup.find('div', class_="mlnew-list")

    for serie_div in table_content.find_all('div', class_='mlnew'):

        try:
            title = serie_div.find('div', class_='mlnh-2').find("h2").get_text(strip=True)
            link = serie_div.find('div', class_='mlnh-2').find('a')['href']
            imdb_rating = serie_div.find('span', class_='mlnh-imdb').get_text(strip=True)

            serie_info = {
                'name': title,
                'url': link,
                'score': imdb_rating
            }

            media_search_manager.add_media(serie_info)

        except:
            pass

    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)
