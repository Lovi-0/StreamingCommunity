# 09.06.24

import logging


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
            url=f"https://{SITE_NAME}.{domain_to_use}/search/?&q={word_to_search}&quick=1&type=videobox_video&nodes=11", 
            headers={'user-agent': get_headers()},
            timeout=max_timeout
        )
        response.raise_for_status()

    except Exception as e:
        console.print(f"Site: {SITE_NAME}, request search error: {e}")

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")
    table_content = soup.find('ol', class_="ipsStream")

    if table_content:
        for title_div in table_content.find_all('li', class_='ipsStreamItem'):
            try:

                title_type = title_div.find("p", class_="ipsType_reset").find_all("a")[-1].get_text(strip=True)
                name = title_div.find("span", class_="ipsContained").find("a").get_text(strip=True)
                link = title_div.find("span", class_="ipsContained").find("a").get("href")

                title_info = {
                    'name': name,
                    'url': link,
                    'type': title_type
                }

                media_search_manager.add_media(title_info)

            except Exception as e:
                logging.error(f"Error processing title div: {e}")

        return media_search_manager.get_length()
    
    else:
        logging.error("No table content found.")
        return -999

    return -9999


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)