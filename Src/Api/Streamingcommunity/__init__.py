# 21.05.24

# Internal utilities
from Src.Util.console import console, msg


# Logic class
from .site import (
    get_version_and_domain,
    title_search,
    get_select_title,
    manager_clear
)

from .film import download_film
from .series import download_series


def main_film_series():
    """
    Main function of the application for film and series.
    """

    # Get site domain and version
    site_version, domain = get_version_and_domain()

    # Make request to site to get content that corrsisponde to that string
    film_search = msg.ask("\n[purple]Insert word to search in all site: ").strip()
    len_database = title_search(film_search, domain)

    if len_database != 0:

        # Select title from list
        select_title = get_select_title()
        
        # For series
        if select_title.type == 'tv':
            download_series(
                tv_id=select_title.id,
                tv_name=select_title.slug, 
                version=site_version, 
                domain=domain
            )
        
        # For film
        else:
            download_film(
                id_film=select_title.id, 
                title_name=select_title.slug, 
                domain=domain
            )
    
    # If no media find
    else:
        console.print("[red]Cant find a single element")
