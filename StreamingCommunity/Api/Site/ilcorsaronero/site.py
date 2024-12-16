# 02.07.24


# Internal utilities
from StreamingCommunity.Util.table import TVShowManager


# Logic class
from StreamingCommunity.Api.Template import get_select_title
from StreamingCommunity.Api.Template.Util import search_domain
from StreamingCommunity.Api.Template.Class.SearchType import MediaManager
from .util.ilCorsarScraper import IlCorsaroNeroScraper


# Variable
from .costant import SITE_NAME
media_search_manager = MediaManager()
table_show_manager = TVShowManager()


async def title_search(word_to_search: str) -> int:
    """
    Search for titles based on a search query.

    Parameters:
        - title_search (str): The title to search for.

    Returns:
        - int: The number of titles found.
    """
    media_search_manager.clear()
    table_show_manager.clear()

    # Find new domain if prev dont work
    domain_to_use, _ = search_domain(SITE_NAME, f"https://{SITE_NAME}")

    # Create scraper and collect result
    print("\n")
    scraper = IlCorsaroNeroScraper(f"https://{SITE_NAME}.{domain_to_use}/", 1)
    results = await scraper.search(word_to_search)

    # Add all result to media manager
    for i, torrent in enumerate(results):
        media_search_manager.add_media({
            'name': torrent['name'],
            'type': torrent['type'],
            'seed': torrent['seed'],
            'leech': torrent['leech'],
            'size': torrent['size'],
            'date': torrent['date'],
            'url': torrent['url']
        })


    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)