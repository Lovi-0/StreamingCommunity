# 09.06.24

# Internal utilities
from Src.Util.console import console, msg


# Logic class
from .site import title_search, get_select_title
from .series import download_series


def search():
    """
    Main function of the application for film and series.
    """

    # Make request to site to get content that corrsisponde to that string
    string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()
    len_database = title_search(string_to_search)

    if len_database > 0:

        # Select title from list
        select_title = get_select_title()

        # Download only film
        download_series(select_title)

    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")
