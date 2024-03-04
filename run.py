# 10.12.23 -> 31.01.24

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
import sys

# [ main ]
def initialize():

    if sys.version_info < (3, 11):
        console.log("Install python version > 3.11")
        sys.exit(0)

    remove_folder("tmp")
    msg_start()

    try:
        main_update()
    except Exception as e:
        console.print(f"[blue]Req github [white]=> [red]Failed: {e}")

    check_ffmpeg()
    print("\n")

def main():

    initialize()
    domain, site_version = Page.domain_version()

    film_search = msg.ask("\n[blue]Search for any movie or tv series title").strip()
    db_title = Page.search(film_search, domain)
    Page.display_search_results(db_title)

    if len(db_title) != 0:
        console.print(f"\n[blue]Total result: {len(db_title)}")
        console.print(
            "\n[green]Insert [yellow]INDEX [red]number [green]or [red][1-2] [green]for a range of movies/tv series or [red][1,3,5] [green]to select discontinued movie/tv series"
        )
        console.print("\n[red]In case of a TV Series you will choose seasons and episodes to download")
        index_select = str(msg.ask("\n[blue]Select [yellow]INDEX [blue]to download"))
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
