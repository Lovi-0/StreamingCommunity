# 10.12.23

import sys
import json
import logging


# External libraries
import requests
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.table import TVShowManager
from Src.Util.headers import get_headers
from Src.Util.console import console
from Src.Util.config import config_manager
from .Class import MediaManager, MediaItem


# Config
GET_TITLES_OF_MOMENT = config_manager.get_bool('DEFAULT', 'get_moment_title')


# Variable
media_search_manager = MediaManager()
table_show_manager = TVShowManager()


def get_token(site_name: str, domain: str) -> dict:
    """
    Function to retrieve session tokens from a specified website.

    Args:
    - site_name (str): The name of the site.
    - domain (str): The domain of the site.

    Returns:
    - dict: A dictionary containing session tokens.
      The keys are 'XSRF_TOKEN', 'animeunity_session', and 'csrf_token'.
    """

    # Create a session object to handle the HTTP request and response
    session = requests.Session()

    # Send a GET request to the specified URL composed of the site name and domain
    response = session.get(f"https://www.{site_name}.{domain}")

    # Initialize variables to store CSRF token
    find_csrf_token = None
    
    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.text, "lxml")
    
    # Loop through all meta tags in the HTML response
    for html_meta in soup.find_all("meta"):

        # Check if the meta tag has a 'name' attribute equal to "csrf-token"
        if html_meta.get('name') == "csrf-token":

            # If found, retrieve the content of the meta tag, which is the CSRF token
            find_csrf_token = html_meta.get('content')

    return {
        'XSRF_TOKEN': session.cookies['XSRF-TOKEN'],
        'animeunity_session': session.cookies['animeunity_session'],
        'csrf_token': find_csrf_token
    }


def get_moment_titles(domain: str, version: str, prefix: str):
    """
    Retrieves the title name from a specified domain using the provided version and prefix.

    Args:
    - domain (str): The domain of the site
    - version (str): The version of the site
    - prefix (str): The prefix used for retrieval. [film or serie-tv or "" for site]

    Returns:
    - str or None: The title name if retrieval is successful, otherwise None.
    """
    try:

        headers = {
            'x-inertia': 'true',
            'x-inertia-version': version,
            'user-agent': get_headers()
        }

        response = requests.get(f'https://streamingcommunity.{domain}/{prefix}', headers=headers)

 
        if response.ok:

            # Extract title name
            title_name = response.json()['props']['title']['name']

            # Return
            return title_name 
        
        else:
            logging.error("Failed to retrieve data. Status code: %d", response.status_code)
            return None
        
    except Exception as e:
        logging.error("Error occurred: %s", str(e))
        return None


def get_domain() -> str:
    """
    Fetches the domain from a Telegra.ph API response.

    Returns:
        str: The domain extracted from the API response.
    """
    console.print("[cyan]Make request api [white]...")

    try:
        response = requests.get("https://api.telegra.ph/getPage/Link-Aggiornato-StreamingCommunity-01-17", headers={'user-agent': get_headers()})
        console.print(f"[green]Request response [white]=> [red]{response.status_code} \n")
        response.raise_for_status()  # Raise an error if request fails

        if response.ok:

            domain = response.json()['result']['description'].split(".")[1]
            return domain
        
    except Exception as e:
        logging.error(f"Error fetching domain: {e}")
        sys.exit(0)


def test_site(domain: str) -> str:
    """
    Tests the availability of a website.

    Args:
        domain (str): The domain to test.

    Returns:
        str: The response text if successful, otherwise None.
    """
    
    console.print("[cyan]Make request site [white]...")
    site_url = f"https://streamingcommunity.{domain}"

    try:
        response = requests.get(site_url, headers={'user-agent': get_headers()})
        console.print(f"[green]Request response [white]=> [red]{response.status_code} \n")
        response.raise_for_status()  # Raise an error if request fails

        if response.ok:
            return response.text
        else:
            return None
        
    except Exception as e:
        logging.error(f"Error testing site: {e}")
        return None


def get_version(text: str) -> str:
    """
    Extracts the version from the HTML text of a webpage.

    Args:
        text (str): The HTML text of the webpage.

    Returns:
        str: The version extracted from the webpage.
    """
    console.print("[cyan]Make request to get version [white]...")

    try:
        soup = BeautifulSoup(text, "html.parser")
        version = json.loads(soup.find("div", {"id": "app"}).get("data-page"))['version']
        console.print(f"[green]Request response [white]=> [red]200 \n")

        return version
    
    except Exception as e:
        logging.error(f"Error extracting version: {e}")
        sys.exit(0)


def get_version_and_domain() -> tuple[str, str]:
    """
    Retrieves the version and domain of a website.

    Returns:
        tuple[str, str]: A tuple containing the version and domain.
    """

    try:
        config_domain = config_manager.get('SITE', 'streaming_domain')

        response_test_site = test_site(config_domain)

        if response_test_site is None:
            config_domain = get_domain()
            response_test_site = test_site(config_domain)

        if response_test_site:
            version = get_version(response_test_site)

            # Update domain config file
            config_manager.set_key('SITE', 'streaming_domain', str(config_domain))
            config_manager.write_config()

            # Get titles in the moment
            if GET_TITLES_OF_MOMENT:
                console.print("[cyan]Scrape information [white]...")
                console.print(f"[green]Title of the moments: [purple]{get_moment_titles(config_domain, version, '')}")
                console.print(f"[green]Film of the moments: [purple]{get_moment_titles(config_domain, version, 'film')}")
                console.print(f"[green]Serie of the moments: [purple]{get_moment_titles(config_domain, version, 'serie-tv')}")

            return version, config_domain
        
        else:
            print("Can't connect to site")
            sys.exit(0)

    except Exception as e:
        logging.error(f"Error getting version and domain: {e}")
        sys.exit(0)


def search(title_search: str, domain: str) -> int:
    """
    Search for titles based on a search query.

    Args:
        title_search (str): The title to search for.
        domain (str): The domain to search on.

    Returns:
        int: The number of titles found.
    """
    
    # Send request to search for titles
    req = requests.get(f"https://streamingcommunity.{domain}/api/search?q={title_search}", headers={'user-agent': get_headers()})

    # Add found titles to media search manager
    for dict_title in req.json()['data']:
        media_search_manager.add_media(dict_title)

    # Return the number of titles found
    return media_search_manager.get_length()


def update_domain_anime():
    """
    Update the domain for anime streaming site.
    """

    # Read actual config
    url_site_name = config_manager.get('SITE', 'anime_site_name')  
    url_domain = config_manager.get('SITE', 'anime_domain')  

    # Test actual site 
    test_response = requests.get(f"https://www.{url_site_name}.{url_domain}")
    console.print(f"[green]Request test response [white]=> [red]{test_response.status_code} \n")

    if not test_response.ok:

        # Update streaming domain
        version, domain = get_version_and_domain()

        # Extract url
        response = requests.get(f"https://streamingcommunity.{domain}/")
        soup = BeautifulSoup(response.text, "html.parser")

        # Found the anime site link
        new_site_url = None
        for html_a in soup.find_all("a"):
            if config_manager.get('SITE', 'anime_site_name') in str(html_a.get("href")):
                new_site_url = html_a.get("href")

        # Extract the domain from the URL and update the config
        config_manager.set_key('SITE', 'anime_domain', new_site_url.split(".")[-1])


def anime_search(title_search: str) -> int:
    """
    Function to perform an anime search using a provided title.

    Args:
    - title_search (str): The title to search for.

    Returns:
    - int: A number containing the length of media search manager.
    """

    # Update domain
    update_domain_anime()

    # Get token and session value from configuration
    url_site_name = config_manager.get('SITE', 'anime_site_name')  
    url_domain = config_manager.get('SITE', 'anime_domain')  
    data = get_token(url_site_name, url_domain)

    # Prepare cookies to be used in the request
    cookies = {
        'animeunity_session': data.get('animeunity_session')  # Use the session token retrieved from data
    }

    # Prepare headers for the request
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json;charset=UTF-8',
        'x-csrf-token': data.get('csrf_token')  # Use the CSRF token retrieved from data
    }

    # Prepare JSON data to be sent in the request
    json_data = {
        'title': title_search  # Use the provided title for the search
    }

    # Send a POST request to the API endpoint for live search
    response = requests.post(f'https://www.{url_site_name}.{url_domain}/livesearch', cookies=cookies, headers=headers, json=json_data)

    # Process each record returned in the response
    for record in response.json()['records']:

        # Rename keys for consistency
        record['name'] = record.pop('title')  
        record['last_air_date'] = record.pop('date')  

        # Add the record to media search manager if the name is not None
        if record['name'] is not None:
            media_search_manager.add_media(record)

    # Return the length of media search manager
    return media_search_manager.get_length()


def get_select_title() -> MediaItem:
    """
    Display a selection of titles and prompt the user to choose one.

    Returns:
        MediaItem: The selected media item.
    """

    # Set up table for displaying titles
    table_show_manager.set_slice_end(10)

    # Add columns to the table
    column_info = {
        "Index": {'color': 'red'},
        "Name": {'color': 'magenta'},
        "Type": {'color': 'yellow'},
        "Score": {'color': 'cyan'},
        "Date": {'color': 'green'}
    }
    table_show_manager.add_column(column_info)

    # Populate the table with title information
    for i, media in enumerate(media_search_manager.media_list):
        table_show_manager.add_tv_show({
            'Index': str(i),
            'Name': media.name,
            'Type': media.type,
            'Score': media.score,
            'Date': media.last_air_date
        })

    # Run the table and handle user input
    last_command = table_show_manager.run(force_int_input=True, max_int_input=len(media_search_manager.media_list))

    # Handle user's quit command
    if last_command == "q":
        console.print("\n[red]Quit [white]...")
        sys.exit(0)

    # Check if the selected index is within range
    if 0 <= int(last_command) <= len(media_search_manager.media_list):
        return media_search_manager.get(int(last_command))
    else:
        console.print("\n[red]Wrong index")
        sys.exit(0)
