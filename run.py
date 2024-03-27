# 10.12.23 -> 1.02.24

# Class
import Src.Api.page as Page
from Src.Api.film import main_dw_film as download_film
from Src.Api.tv import main_dw_tv as download_tv
from Src.Util.message import msg_start
from Src.Util.console import console, msg
from Src.Util.os import remove_folder
from Src.Upload.update import main_update
from Src.Lib.FFmpeg.installer import check_ffmpeg

# Import
import sys, platform

def initialize():
    """
    Initializes the application by performing necessary setup tasks.
    """

    # Get system where script is run
    run_system = platform.system()

    # Checking Python version
    if sys.version_info < (3, 11):
        console.log("Install python version > 3.11")
        sys.exit(0)

    # Removing temporary folder
    remove_folder("tmp")
    msg_start()

    try:
        # Updating application
        main_update()
    except Exception as e:
        console.print(f"[blue]Request GitHub [white]=> [red]Failed: {e}")

    # Checking FFmpeg installation
    if run_system != 'Windows':
        check_ffmpeg()
    
    print("\n")


def main():
    """
    Main function to execute the application logic.
    """

    # Initializing the application
    initialize()

    # Retrieving domain and site version
    domain, site_version = Page.domain_version()

    # Searching for movie or TV series title
    film_search = msg.ask("\n[blue]Search for any Movie or TV Series title").strip()
    db_title = Page.search(film_search, domain)
    Page.display_search_results(db_title)

    if db_title:

        # Displaying total results
        console.print(f"\n[blue]Total result: {len(db_title)}")

        # Asking user to select title(s) to download
        console.print(
            "\n[green]Insert [yellow]INDEX [red]number[green], or [red][1-2] [green]for a range of movies/tv series, or [red][1,3,5] [green]to select discontinued movie/tv series"
        )
        console.print("\n[red]In case of a TV Series you will also choose seasons and episodes to download")
        index_select = str(msg.ask("\n[blue]Select [yellow]INDEX [blue]to download")).strip()

        # For only number ( to fix )
        if index_select.isnumeric():
            index_select = int(index_select)
            if 0 <= index_select <= len(db_title) - 1:
                selected_title = db_title[index_select]

                if selected_title['type'] == "movie":
                    console.print(f"[green]\nSelected Movie: {selected_title['name']}")
                    download_film(selected_title['id'], selected_title['slug'], domain)
                else:
                    console.print(f"[green]\nSelected TV Series: {selected_title['name']}")
                    download_tv(selected_title['id'], selected_title['slug'], site_version, domain)
            else:
                console.print("[red]Wrong INDEX for selection")

        # For range like [5-15] ( to fix )
        elif "[" in index_select:
            if "-" in index_select:
                start, end = map(int, index_select[1:-1].split('-'))
                result = list(range(start, end + 1))
                for n in result:
                    selected_title = db_title[n]
                    if selected_title['type'] == "movie":
                        console.print(f"[green]\nSelected Movie: {selected_title['name']}")
                        download_film(selected_title['id'], selected_title['slug'], domain)
                    else:
                        console.print(f"[green]\nSelected TV Series: {selected_title['name']}")
                        download_tv(selected_title['id'], selected_title['slug'], site_version, domain)

            # For a list of specific ( to fix )
            elif "," in index_select:
                result = list(map(int, index_select[1:-1].split(',')))
                for n in result:
                    selected_title = db_title[n]
                    if selected_title['type'] == "movie":
                        console.print(f"[green]\nSelected Movie: {selected_title['name']}")
                        download_film(selected_title['id'], selected_title['slug'], domain)
                    else:
                        console.print(f"[green]\nSelected TV Series: {selected_title['name']}")
                        download_tv(selected_title['id'], selected_title['slug'], site_version, domain)
            else:
                console.print("[red]Wrong INDEX for selection")
    else:
        console.print("[red]Couldn't find any entries for the selected title")

    console.print("[red]Done!")

if __name__ == '__main__':

    main()

    while 1:
        cmd_insert = str(msg.ask("[red]Quit the script ? [red][[yellow]yes[red] / [yellow]no[red]]"))

        if cmd_insert in ['y', 'yes', 'ye']:
            break
        else:
            main()
