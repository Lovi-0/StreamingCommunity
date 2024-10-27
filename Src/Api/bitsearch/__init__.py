# 01.07.24

# Internal utilities
from Src.Util.console import console, msg


# Logic class
from .site import title_search, run_get_select_title
from .title import download_title


# Variable
indice = 7
_use_for = "film_serie"
_deprecate = False


def search():
    """
    Main function of the application for film and series.
    """

    # Make request to site to get content that corrsisponde to that string
    string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()
    len_database = title_search(string_to_search)

    if len_database > 0:

        # Select title from list
        select_title = run_get_select_title()

        # Download title
        download_title(select_title)


    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")

        # Retry
        search()
