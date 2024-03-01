# 10.12.23

# Class import
from Src.Util.headers import get_headers
from Src.Util.console import console

# General import
import requests, sys, json
from bs4 import BeautifulSoup


def domain_version():
    domain_req = requests.get("https://api.telegra.ph/getPage/Link-Aggiornato-StreamingCommunity-01-17")
    domain = domain_req.json()['result']['description'].split(".")[1]
    console.print("[green]Get rules ...")

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
        sys.exit(0)


def search(title_search, domain):
    req = requests.get(f"https://streamingcommunity.{domain}/api/search?q={title_search}", headers={'user-agent': get_headers()})

    if req.ok:
        return [{'name': title['name'], 'type': title['type'], 'id': title['id'], 'slug': title['slug']} for title in
                req.json()['data']][0:21]
    else:
        console.log(f"[red]Error: {req.status_code}")
        sys.exit(0)


def display_search_results(db_title):
    for i, title in enumerate(db_title):
        console.print(f"[yellow]{i} [white]-> [green]{title['name']} [white]- [cyan]{title['type']}")
