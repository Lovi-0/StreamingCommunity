# 10.12.23

# Class import
from Src.Util.headers import get_headers
from Src.Util.console import console

# General import
import requests, sys, json
from bs4 import BeautifulSoup

def domain_version():
    console.print("[green]Get rules ...")
    req_repo = None
    try:
        with open('data.json', 'r') as file:
            req_repo = json.load(file)
    except FileNotFoundError:
        req_repo = {"domain": ""}
    domain = req_repo['domain']

    while True:
        if not domain:
            domain = input("Insert domain (streamingcommunity.?): ")
            req_repo['domain'] = domain
            with open('data.json', 'w') as file:
                json.dump(req_repo, file)
        console.print(f"[blue]Test domain [white]=> [red]{domain}")
        site_url = f"https://streamingcommunity.{domain}"
        try:
            site_request = requests.get(site_url, headers={'user-agent': get_headers()})
            soup = BeautifulSoup(site_request.text, "lxml")
            version = json.loads(soup.find("div", {"id": "app"}).get("data-page"))['version']
            console.print(f"[blue]Rules [white]=> [red].{domain}")
            return domain, version
        
        except Exception as e:
            console.log("[red]Cant get version, problem with domain. Try again.")
            domain = None
            continue

def search(title_search, domain):

    req = requests.get(f"https://streamingcommunity.{domain}/api/search?q={title_search}", headers={'user-agent': get_headers()})

    if req.ok:
        return [{'name': title['name'], 'type': title['type'], 'id': title['id'], 'slug': title['slug']} for title in req.json()['data']][0:21]
    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)

def display_search_results(db_title):
    for i, title in enumerate(db_title):
        console.print(f"[yellow]{i} [white]-> [green]{title['name']} [white]- [cyan]{title['type']}")
