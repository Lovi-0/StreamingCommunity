# 10.12.23

# Class import
from Src.Util.Helper.headers import get_headers
from Src.Util.Helper.console import console

# General import
import requests, sys

def search(title_search, domain):

    title_search = str(title_search).replace(" ", "+")
    req = requests.get(
        url = f"https://streamingcommunity.{domain}/api/search?q={title_search}",
        headers = {"User-agent": get_headers()}
    )

    if req.ok:
        return [{'name': title['name'], 'type': title['type'], 'id': title['id']} for title in req.json()['data']]
    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)