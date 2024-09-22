# 17.09.24

import os
import sys
import logging


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.message import start_message
from Src.Util.console import console
from Src.Util.os import create_folder, can_create_file, remove_special_characters
from Src.Util.headers import get_headers
from Src.Lib.Downloader import HLS_Downloader


# Logic class
from ..Template.Class.SearchType import MediaItem
from ..guardaserie.Player.supervideo import VideoSource
from Src.Lib.TMBD import Json_film


# Config
from .costant import ROOT_PATH, SITE_NAME, DOMAIN_NOW, MOVIE_FOLDER

  

def download_film(movie_details: Json_film):
    """
    Downloads a film using the provided tmbd id.

    Parameters:
        - movie_details (Json_film): Class with info about film title.
    """

    # Start message and display film information
    start_message()
    console.print(f"[yellow]Download:  [red]{movie_details.title} \n")

    # Make request to main site
    url = f"https://{SITE_NAME}.{DOMAIN_NOW}/set-movie-a/{movie_details.imdb_id}"
    response = httpx.get(url, headers={'User-Agent': get_headers()})
    response.raise_for_status()

    # Extract supervideo url
    soup = BeautifulSoup(response.text, "html.parser")
    player_links = soup.find("ul", class_ = "_player-mirrors").find_all("li")
    supervideo_url = "https:" + player_links[0].get("data-link")
    
    # Set domain and media ID for the video source
    video_source = VideoSource()
    video_source.setup(supervideo_url)
    
    # Define output path
    mp4_name = remove_special_characters(movie_details.title) + ".mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, remove_special_characters(movie_details.title))

    # Check if the MP4 file can be created
    if not can_create_file(mp4_name):
        logging.error("Invalid mp4 name.")
        sys.exit(0)

    # Get m3u8 master playlist
    master_playlist = video_source.get_playlist()

    # Download the film using the m3u8 playlist, and output filename
    HLS_Downloader(
        m3u8_playlist = master_playlist,
        output_filename = os.path.join(mp4_path, mp4_name)
    ).start()
