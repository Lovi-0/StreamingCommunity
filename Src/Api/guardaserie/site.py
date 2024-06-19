# 09.06.24

import logging


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.headers import get_headers
from Src.Util.table import TVShowManager
from ..Template import search_domain, get_select_title


# Logic class
from .Core.Class.SearchType import MediaManager


# Variable
from .costant import DOMAIN_NOW
media_search_manager = MediaManager()
table_show_manager = TVShowManager()


def title_search(word_to_search) -> int:
    """
    Search for titles based on a search query.
    """

    # Send request to search for titles
    response = httpx.get(f"https://guardaserie.{DOMAIN_NOW}/?story={word_to_search}&do=search&subaction=search", headers={'user-agent': get_headers()})
    response.raise_for_status()

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