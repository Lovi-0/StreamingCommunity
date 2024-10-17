# 21.05.24

# Internal utilities
from Src.Util.console import console, msg


# Logic class
from .site import title_search, run_get_select_title
from .anime import download_film, download_series


# Variable
indice = 1
_deprecate = False


def search():

    # Make request to site to get content that corrsisponde to that string
    string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()
    len_database = title_search(string_to_search)

    if len_database > 0:

        # Select title from list
        select_title = run_get_select_title()

        if select_title.type == 'Movie':
            download_film(select_title)

        else:
            download_series(select_title)
            
    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")

        # Retry
        search()
