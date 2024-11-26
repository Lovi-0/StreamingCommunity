# 21.05.24

from unidecode import unidecode


# Internal utilities
from StreamingCommunity.Src.Util.console import console, msg


# Logic class
from .site import title_search, run_get_select_title, media_search_manager
from .film_serie import download_film, download_series


# Variable
indice = 1
_useFor = "anime"
_deprecate = False
_priority = 2
_engineDownload = "mp4"


def search(string_to_search: str = None, get_onylDatabase: bool = False):

    if string_to_search is None:
        string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()

    # Search on database
    len_database = title_search(unidecode(string_to_search))

    # Return list of elements
    if get_onylDatabase:
        return media_search_manager

    if len_database > 0:

        # Select title from list (type: TV \ Movie \ OVA)
        select_title = run_get_select_title()

        if select_title.type == 'Movie' or select_title.type == 'OVA':
            download_film(select_title)

        else:
            download_series(select_title)
            
    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")

        # Retry
        search()
