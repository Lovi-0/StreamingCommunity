# 10.12.23

# Class import
from Src.Util.Helper.headers import get_headers
from Src.Util.Helper.console import console

# General import
import requests, json, sys
from bs4 import BeautifulSoup

def get_version(domain):

    try:
        r = requests.get(f'https://streamingcommunity.{domain}/', headers={
            'Authority': f'streamingcommunity.{domain}',
            'User-Agent': get_headers(),
        })
        soup = BeautifulSoup(r.text, "lxml")
        info_data_page = soup.find("div", {'id': 'app'}).attrs["data-page"]

        return json.loads(info_data_page)['version']
    
    except:
        console.log("[red]UPDATE DOMANIN")
        sys.exit(0)
    

def search(title_search, domain):

    title_search = str(title_search).replace(" ", "+")
    r = requests.get(
        url = f"https://streamingcommunity.{domain}/api/search?q={title_search}",
        headers = {"User-agent": get_headers()}
    )

    return [{'name': title['name'], 'type': title['type'], 'id': title['id']} for title in r.json()['data']]
