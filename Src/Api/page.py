# 10.12.23

# Class import
from Src.Util.Helper.headers import get_headers
from Src.Util.Helper.console import console

# General import
import requests, sys

def domain_version():

    req_repo = requests.get("https://raw.githubusercontent.com/Ghost6446/Streaming_comunity_data/main/data.json", headers={'user-agent': get_headers()})

    if req_repo.ok:
        return req_repo.json()['domain'], req_repo.json()['version']
    
    else:
        console.log(f"[red]Error: {req_repo.status_code}")
        sys.exit(0)

def search(title_search, domain):

    req = requests.get(f"https://streamingcommunity.{domain}/api/search?q={title_search}", headers={'user-agent': get_headers()})

    if req.ok:
        return [{'name': title['name'], 'type': title['type'], 'id': title['id'], 'slug': title['slug']} for title in req.json()['data']]
    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)