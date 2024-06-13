# 09.06.24

import os
import sys
import logging
from urllib.parse import urlparse


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.message import start_message
from Src.Util.color import Colors
from Src.Util.console import console, msg
from Src.Util.os import create_folder, can_create_file
from Src.Util._jsonConfig import config_manager
from Src.Util.headers import get_headers
from Src.Lib.Hls.download_mp4 import MP4_downloader


# Config
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
from .costant import MAIN_FOLDER, MOVIE_FOLDER


# Variable
cookie_index = config_manager.get_dict('REQUESTS', 'index')


def search() -> int:
    """
    Search for titles based on a search query.
    """

    print()
    url_search = msg.ask(f"[cyan]Insert url title")

    # Send request to search for titles
    try:
        response = httpx.get(url_search, headers={'user-agent': get_headers()}, cookies=cookie_index)
        response.raise_for_status()

    except Exception as e:
        logging.error("Insert: {'ips4_IPSSessionFront': 'your_code', 'ips4_member_id': 'your_code'} in config file \ REQUESTS \ index, instead of user-agent. Use browser debug and cookie request with a valid account.")
        sys.exit(0)

    # Create soup and mp4 video
    soup = BeautifulSoup(response.text, "html.parser")
    souce = soup.find("source")

    # Get url and filename
    try:
        mp4_link = souce.get("src")

    except Exception as e:
        logging.error("Insert: {'ips4_IPSSessionFront': 'your_code', 'ips4_member_id': 'your_code'} in config file \ REQUESTS \ index, instead of user-agent. Use browser debug and cookie request with a valid account.")
        sys.exit(0)
    
    parsed_url = urlparse(url_search)
    path_parts = parsed_url.path.split('/')
    mp4_name = path_parts[-2] if path_parts[-1] == '' else path_parts[-1] + ".mp4"

    # Create destination folder
    mp4_path = os.path.join(ROOT_PATH, MAIN_FOLDER, MOVIE_FOLDER)

    # Check if can create file output
    create_folder(mp4_path)                                                                    
    if not can_create_file(mp4_name):  
        logging.error("Invalid mp4 name.")
        sys.exit(0)

    # Start download
    start_message()
    MP4_downloader(
        url = mp4_link, 
        path = os.path.join(mp4_path, mp4_name),
        referer = f"{parsed_url.scheme}://{parsed_url.netloc}/",
        add_desc=f"{Colors.MAGENTA}video"
    )
