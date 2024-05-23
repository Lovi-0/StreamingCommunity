# 15.05.24

# Fix import
import sys
import os
import logging
from urllib.parse import urlencode
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Library import
from Src.Lib.Request import requests
import time
import json
import re
import html

from datetime import datetime


def get_current_expiration_timestamp():
    """Get the current Unix timestamp."""
    return int(time.time())

def get_current_year_month():
    """Get the current year and month."""
    now = datetime.now()
    return now.year, now.month

def create_json_file():
    """Create a JSON file if it does not exist."""
    if not os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump({}, file, indent=4)

def save_playlist_info(year, month, playlist_info):
    """
    Save playlist information for a specific year and month.

    Args:
        year (int): The year.
        month (int): The month.
        playlist_info (dict): Information about the playlist.
    """
    logging.info(f"Saving playlist info for {year}-{month}")
    with open(JSON_FILE_PATH, 'r') as file:
        data = json.load(file)

    year_month_key = f"{year}-{month}"
    data[year_month_key] = playlist_info

    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)



# Variable
year, month = get_current_year_month()
JSON_FILE_PATH = 'playlist_info.json'


def load_playlist_info(year, month):
    """
    Load playlist information for a specific year and month.

    Args:
        year (int): The year.
        month (int): The month.

    Returns:
        dict: Information about the playlist for the specified year and month, or None if not found.
    """
    logging.info(f"Loading playlist info for {year}-{month}")
    if not os.path.exists(JSON_FILE_PATH):
        return None

    with open(JSON_FILE_PATH, 'r') as file:
        data = json.load(file)

    year_month_key = f"{year}-{month}"
    return data.get(year_month_key)

def _fetch_webpage_text(url):
    """
    Fetch webpage text from a given URL.

    Args:
        url (str): The URL of the webpage.

    Returns:
        str: The text content of the webpage.
    """
    logging.info(f"Fetching webpage text from URL: {url}")
    response = requests.get(url, timeout=3)
    response.raise_for_status() 
    return html.unescape(response.text)

def _extract_playlist_info(webpage_text):
    """
    Extract playlist information from webpage text.

    Args:
        webpage_text (str): The text content of the webpage.

    Returns:
        dict: Information about the playlist extracted from the webpage.
    """
    logging.info("Extracting playlist info from webpage text")
    info_match = re.search(r'data-page="([\s\S]+})"', webpage_text)
    info_data = info_match.group(1)

    print("1. =>", info_data)
    info = json.loads(info_data)
    logging.debug(f"Playlist info extracted: {info}")
    return info

def _extract_iframe_info(playlist_info):
    """
    Extract iframe info from playlist information.

    Args:
        playlist_info (dict): Information about the playlist.

    Returns:
        str: The text content of the iframe.
    """
    embed_url = playlist_info['props']['embedUrl']
    logging.info(f"Fetching iframe info from embed URL: {embed_url}")
    iframe_text = _fetch_webpage_text(embed_url)
    iframe_info_url_match = re.search(r'<iframe[^>]+src="([^"]+)', iframe_text)
    iframe_info_url = iframe_info_url_match.group(1)

    print("2. =>", iframe_info_url)
    return _fetch_webpage_text(iframe_info_url)

def _extract_playlist_url(iframe_info_text):
    """
    Extract playlist URL from iframe info text.

    Args:
        iframe_info_text (str): The text content of the iframe.

    Returns:
        tuple: A tuple containing playlist information and the playlist URL.
    """
    logging.info("Extracting playlist URL from iframe info text")
    playlist_match = re.search(r'window\.masterPlaylist[^:]+params:[^{]+({[^<]+?})', iframe_info_text)
    playlist_info = json.loads(re.sub(r',[^"]+}', '}', playlist_match.group(1).replace('\'', '"')))

    playlist_url_match = re.search(r'window\.masterPlaylist[^<]+url:[^<]+\'([^<]+?)\'', iframe_info_text)
    playlist_url = playlist_url_match.group(1)
    
    logging.debug(f"Playlist info: {playlist_info}, Playlist URL: {playlist_url}")
    return playlist_info, playlist_url

def _construct_download_url(playlist_info, playlist_url):
    """
    Construct download URL from playlist information and URL.

    Args:
        playlist_info (dict): Information about the playlist.
        playlist_url (str): The URL of the playlist.

    Returns:
        str: The constructed download URL.
    """
    logging.info("Constructing download URL")
    year, month = get_current_year_month()
    save_playlist_info(year, month, playlist_info)
    query = urlencode(list(playlist_info.items()))
    dl_url = playlist_url + '?' + query
    logging.debug(f"Download URL constructed: {dl_url}")
    return dl_url

def get_download_url(video_url):
    """
    Get the download URL for a video from its URL.

    Args:
        video_url (str): The URL of the video.

    Returns:
        str: The download URL for the video.
    """
    logging.info(f"Getting download URL for video: {video_url}")
    webpage_text = _fetch_webpage_text(video_url)
    playlist_info = _extract_playlist_info(webpage_text)
    scws_id = playlist_info['props']['title']['scws_id']

    # Get episode scws_id
    if scws_id is None: 
        logging.info("Getting id from series")
        scws_id = playlist_info['props']['episode']['scws_id']
    else:
        logging.info("Getting id from film")

    loaded_parameter = load_playlist_info(year, month)
    if loaded_parameter is None:
        iframe_info_text = _extract_iframe_info(playlist_info)
        playlist_info, playlist_url = _extract_playlist_url(iframe_info_text)
        return _construct_download_url(playlist_info, playlist_url)
    
    else:
        playlist_url = f"https://vixcloud.co/playlist/{scws_id}?{urlencode(list(loaded_parameter.items()))}"
        return playlist_url

if __name__ == "__main__":

    # Create json file
    create_json_file()

    # Get m3u8 playlist from watch url
    video_url = "https://streamingcommunity.foo/watch/8427?e=61248"
    download_url = get_download_url(video_url)
    print(download_url)
