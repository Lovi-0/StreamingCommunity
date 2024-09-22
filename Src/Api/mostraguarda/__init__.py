# 26.05.24

# Internal utilities
from Src.Util.console import console, msg


# Logic class
from Src.Lib.TMBD import tmdb, Json_film
from .film import download_film


# Variable
indice = 9
_deprecate = False


def search():
    """
    Main function of the application for film and series.
    """

    # Make request to site to get content that corrsisponde to that string
    string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()
    movie_id = tmdb.search_movie(string_to_search)

    if movie_id:
        movie_details: Json_film = tmdb.get_movie_details(tmdb_id=movie_id)

        # Download only film
        download_film(movie_details)

    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")

        # Retry
        search()
