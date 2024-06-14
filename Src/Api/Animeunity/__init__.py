# 21.05.24

# Internal utilities
from Src.Util.console import console, msg


# Logic class
from .site import title_search, get_select_title
from .anime import donwload_film, donwload_series


def search():

    # Make request to site to get content that corrsisponde to that string
    string_to_search = msg.ask("\n[purple]Insert word to search in all site").strip()
    len_database = title_search(string_to_search)

    if len_database > 0:

        # Select title from list
        select_title = get_select_title()
        
        if select_title.type == 'TV':
            donwload_series(
                tv_id=select_title.id,
                tv_name=select_title.slug
            )

        else:
            donwload_film(
                id_film=select_title.id, 
                title_name=select_title.slug
            )

    else:
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")
