# 26.05.24

# Internal utilities
from Src.Util.console import console, msg


# Logic class
from .site import (
    title_search,
    get_select_title,
    manager_clear
)

from .film import download_film


def search():
    """
    Main function of the application for film and series.
    """

    # Make request to site to get content that corrsisponde to that string
    film_search = msg.ask("\n[purple]Insert word to search in all site").strip()
    len_database = title_search(film_search)

    if len_database != 0:

        # Select title from list
        select_title = get_select_title()

        # Download only film
        download_film(
            title_name=select_title.name,
            url=select_title.url
        )

