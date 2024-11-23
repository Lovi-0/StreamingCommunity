# 09.06.24

from unidecode import unidecode


# Internal utilities
from StreamingCommunity.Src.Util.console import console, msg


# Logic class
from .site import title_search, run_get_select_title, media_search_manager
from .film import download_film


# Variable
indice = 9
_useFor = "film"
_deprecate = False
_priority = 2
_engineDownload = "mp4"


def search(string_to_search: str = None, get_onylDatabase: bool = False):
    """
    Main function of the application for film and series.
    """

    if string_to_search is None:
        string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()

    # Search on database
    len_database = title_search(unidecode(string_to_search))

    # Return list of elements
    if get_onylDatabase:
        return media_search_manager
    
    if len_database > 0:

        # Select title from list
        select_title = run_get_select_title()

        # !!! ADD TYPE DONT WORK FOR SERIE
        download_film(select_title)


    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")

        # Retry
        search()
