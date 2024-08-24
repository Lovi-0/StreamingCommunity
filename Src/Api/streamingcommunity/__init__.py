# 21.05.24

# Internal utilities
from Src.Util.console import console, msg


# Logic class
from .site import get_version_and_domain, title_search, run_get_select_title
from .film import download_film
from .series import download_series


# Variable
indice = 0
_deprecate = False


def search():
    """
    Main function of the application for film and series.
    """

    # Make request to site to get content that corrsisponde to that string
    string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()

    # Get site domain and version and get result of the search
    site_version, domain = get_version_and_domain()
    len_database = title_search(string_to_search, domain)

    if len_database > 0:

        # Select title from list
        select_title = run_get_select_title()
        
        if select_title.type == 'tv':
            download_series(select_title, domain, site_version)
        
        else:
            download_film(select_title, domain, site_version)
    
    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")

        # Retry
        search()
