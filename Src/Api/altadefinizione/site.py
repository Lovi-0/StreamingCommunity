# 26.05.24

# External libraries
import httpx
from bs4 import BeautifulSoup
from unidecode import unidecode


# Internal utilities
from Src.Util.console import console
from Src.Util._jsonConfig import config_manager
from Src.Util.headers import get_headers
from Src.Util.table import TVShowManager
from ..Template import search_domain, get_select_title
from ..Template.Class.SearchType import MediaManager


# Variable
from .costant import SITE_NAME
media_search_manager = MediaManager()
table_show_manager = TVShowManager()


def title_search(title_search: str) -> int:
    """
    Search for titles based on a search query.

    Parameters:
        - title_search (str): The title to search for.

    Returns:
        int: The number of titles found.
    """

    # Find new domain if prev dont work
    max_timeout = config_manager.get_int("REQUESTS", "timeout")
    domain_to_use, _ = search_domain(SITE_NAME, f"https://{SITE_NAME}")
    
    # Send request to search for title
    try:
        response = httpx.get(
            url=f"https://{SITE_NAME}.{domain_to_use}/?story={unidecode(title_search.replace(' ', '+'))}&do=search&subaction=search&titleonly=3", 
            headers={'user-agent': get_headers()},
            timeout=max_timeout
        )
        response.raise_for_status()

    except Exception as e:
        console.print(f"Site: {SITE_NAME}, request search error: {e}")

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")
    table_content = soup.find('div', id="dle-content")

    # Scrape div film in table on single page
    for film_div in table_content.find_all('div', class_='col-lg-3'):
        title = film_div.find('h2', class_='titleFilm').get_text(strip=True)
        link = film_div.find('h2', class_='titleFilm').find('a')['href']
        imdb_rating = film_div.find('div', class_='imdb-rate').get_text(strip=True).split(":")[-1]

        film_info = {
            'name': title,
            'url': link,
            'score': imdb_rating
        }

        media_search_manager.add_media(film_info)

    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)
