# 10.12.23

# Class import
import Src.Api.page as Page
from Src.Api.film import main_dw_film as download_film
from Src.Api.tv import main_dw_tv as download_tv
from Src.Util.Helper.message import msg_start
from Src.Util.Helper.console import console, msg
from Src.Upload.update import main_update

# General import
import sys

# Variable
domain = "cz"
site_version = Page.get_version(domain)

def main():

    msg_start()
    main_update()
    console.print(f"[blue]Find system [white]=> [red]{sys.platform} \n")
    
    film_search = msg.ask("\n[blue]Insert word to search in all site: ").strip()
    db_title = Page.search(film_search, domain)

    for i in range(len(db_title)):
        console.print(f"[yellow]{i} [white]-> [green]{db_title[i]['name']} [white]- [cyan]{db_title[i]['type']}")
    index_select = int(msg.ask("\n[blue]Index to download: "))

    if db_title[index_select]['type'] == "movie":
        console.print(f"[green]\nMovie select: {db_title[index_select]['name']}")
        download_film(db_title[index_select]['id'], db_title[index_select]['name'].replace(" ", "+"), domain)

    else:
        console.print(f"[green]\nTv select: {db_title[index_select]['name']}")
        download_tv(db_title[index_select]['id'], db_title[index_select]['name'].replace(" ", "+"), site_version, domain)

    console.print("\n[red]Done")

if __name__ == '__main__':
    main()