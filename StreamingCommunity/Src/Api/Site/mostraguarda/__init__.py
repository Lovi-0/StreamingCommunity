# 26.05.24

from unidecode import unidecode


# Internal utilities
from StreamingCommunity.Src.Util.console import console, msg


# Logic class
from StreamingCommunity.Src.Lib.TMBD import tmdb, Json_film
from .film import download_film


# Variable
indice = 9
_useFor = "film"
_deprecate = False
_priority = 2
_engineDownload = "hls"


def search(string_to_search: str = None, get_onylDatabase: bool = False):
    """
    Main function of the application for film and series.
    """

    if string_to_search is None:
        string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()

    # Not available for the moment
    if get_onylDatabase:
        return 0

    # Search on database
    movie_id = tmdb.search_movie(unidecode(string_to_search))

    if movie_id is not None:
        movie_details: Json_film = tmdb.get_movie_details(tmdb_id=movie_id)

        # Download only film
        download_film(movie_details)

    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")

        # Retry
        search()
