# 02.12.24

from datetime import datetime
from typing import List, Dict


# External
import httpx


# Util
from StreamingCommunity.Util.headers import get_headers
from StreamingCommunity.Util.console import console, msg
from StreamingCommunity.Util._jsonConfig import config_manager


# Internal
from StreamingCommunity.Api.Site.streamingcommunity.costant import SITE_NAME
from StreamingCommunity.Api.Site.streamingcommunity.site import get_version_and_domain


# Variable
max_timeout = 10
 

def search_titles(title_search: str, domain: str) -> List[Dict]:
    """
    Searches for content using an API based on a title and domain.

    Args:
        title_search (str): The title to search for.
        domain (str): The domain of the API site to query.

    Returns:
        List[Dict[str, str | int]]: A list of dictionaries containing information about the found content.
    """
    titles = []

    try:
        url = f"https://{SITE_NAME}.{domain}/api/search?q={title_search.replace(' ', '+')}"

        response = httpx.get(
            url=url,
            headers={'user-agent': get_headers()},
            timeout=max_timeout
        )

        response.raise_for_status()

    except:
        console.print(f"[red]Error: {response.status_code}")
        return []

    for dict_title in response.json().get('data', []):
        if dict_title.get('last_air_date'):
            release_year = datetime.strptime(dict_title['last_air_date'], '%Y-%m-%d').year
        else:
            release_year = ''

        images = {}
        for dict_image in dict_title.get('images', []):
            images[dict_image.get('type')] = f"https://cdn.{SITE_NAME}.{domain}/images/{dict_image.get('filename')}"
    
        titles.append({
            'id': dict_title.get("id", ""),
            'slug': dict_title.get("slug", ""),
            'name': dict_title.get("name", ""),
            'type': dict_title.get("type", ""),
            'seasons_count': dict_title.get("seasons_count", 0),
            'year': release_year,
            'images': images,
            'url': f"https://{SITE_NAME}.{domain}/titles/{dict_title.get('id')}-{dict_title.get('slug')}"
        })

    return titles

def get_infoSelectTitle(url_title: str, domain: str, version: str):

    headers = {
        'user-agent': get_headers(),
        'x-inertia': 'true',
        'x-inertia-version': version
    }

    response = httpx.get(url_title, headers=headers, timeout=10)

    if response.status_code == 200:
        json_response = response.json()['props']

        images = {}
        for dict_image in json_response['title'].get('images', []):
            images[dict_image.get('type')] = f"https://cdn.{SITE_NAME}.{domain}/images/{dict_image.get('filename')}"

        rsp = {
            'id': json_response['title']['id'],
            'name': json_response['title']['name'],
            'slug': json_response['title']['slug'],
            'plot': json_response['title']['plot'],
            'type': json_response['title']['type'],
            'season_count': json_response['title']['seasons_count'],
            'image': images
        }

        if json_response['title']['type'] == 'tv':
            season = json_response["loadedSeason"]["episodes"]
            episodes = []

            for e in season:
                episode = {
                    "id": e["id"],
                    "number": e["number"],
                    "name":  e["name"],
                    "plot": e["plot"],
                    "duration": e["duration"],
                    "image": f"https://cdn.{SITE_NAME}.{domain}/images/{e['images'][0]['filename']}"
                }
                episodes.append(episode)

            rsp["episodes"] = episodes

        return rsp
        
    else:
        return []
    
def get_infoSelectSeason(url_title: str, number_season: int, domain: str, version: str):

    headers = {
        'user-agent': get_headers(),
        'x-inertia': 'true',
        'x-inertia-version': version
    }

    response = httpx.get(f"{url_title}/stagione-{number_season}", headers=headers, timeout=10)

    json_response = response.json().get('props').get('loadedSeason').get('episodes')
    json_episodes = []

    for json_ep in json_response:
        
        json_episodes.append({
            'id': json_ep.get('id'),
            'number': json_ep.get('number'),
            'name': json_ep.get('name'),
            'plot': json_ep.get('plot'),
            'image': f"https://cdn.{SITE_NAME}.{domain}/images/{json_ep.get('images')[0]['filename']}"
        })

    return json_episodes
