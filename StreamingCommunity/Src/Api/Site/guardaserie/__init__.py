# 09.06.24

from unidecode import unidecode


# Internal utilities
from StreamingCommunity.Src.Util.console import console, msg


# Logic class
from .site import title_search, run_get_select_title, media_search_manager
from .series import download_series


# Variable
indice = 4
_useFor = "serie"
_deprecate = False
_priority = 2
_engineDownload = "hls"


def search(string_to_search: str = None, get_onylDatabase: bool = False):
    """
    Main function of the application for film and series.
    """

    if string_to_search is None:

        # Make request to site to get content that corrsisponde to that string
        string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()
    
    # Search on database
    len_database = title_search(unidecode(string_to_search))

    # Return list of elements
    if get_onylDatabase:
        return media_search_manager

    if len_database > 0:

        # Select title from list
        select_title = run_get_select_title()

        # Download only film
        download_series(select_title)

    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")

        # Retry
        search()
