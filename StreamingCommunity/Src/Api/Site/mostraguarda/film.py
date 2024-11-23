# 17.09.24

import os
import sys
import time
import logging


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from StreamingCommunity.Src.Util.console import console, msg
from StreamingCommunity.Src.Util.os import os_manager
from StreamingCommunity.Src.Util.message import start_message
from StreamingCommunity.Src.Util.call_stack import get_call_stack
from StreamingCommunity.Src.Util.headers import get_headers
from StreamingCommunity.Src.Lib.Downloader import HLS_Downloader


# Logic class
from StreamingCommunity.Src.Api.Template.Util import execute_search


# Player
from StreamingCommunity.Src.Api.Player.supervideo import VideoSource


# TMBD
from StreamingCommunity.Src.Lib.TMBD import Json_film


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
    try:
        url = f"https://{SITE_NAME}.{DOMAIN_NOW}/set-movie-a/{movie_details.imdb_id}"
        response = httpx.get(url, headers={'User-Agent': get_headers()})
        response.raise_for_status()

    except:
        logging.error(f"Not found in the server. Dict: {movie_details}")
        raise

    # Extract supervideo url
    soup = BeautifulSoup(response.text, "html.parser")
    player_links = soup.find("ul", class_ = "_player-mirrors").find_all("li")
    supervideo_url = "https:" + player_links[0].get("data-link")

    
    # Set domain and media ID for the video source
    video_source = VideoSource()
    video_source.setup(supervideo_url)
    
    # Define output path
    title_name = os_manager.get_sanitize_file(movie_details.title) + ".mp4"
    mp4_path = os.path.join(ROOT_PATH, SITE_NAME, MOVIE_FOLDER, title_name.replace(".mp4", ""))

    # Get m3u8 master playlist
    master_playlist = video_source.get_playlist()

    # Download the film using the m3u8 playlist, and output filename
    r_proc = HLS_Downloader(
        m3u8_playlist=master_playlist, 
        output_filename=os.path.join(mp4_path, title_name)
    ).start()

    if r_proc == 404:
        time.sleep(2)

        # Re call search function
        if msg.ask("[green]Do you want to continue [white]([red]y[white])[green] or return at home[white]([red]n[white]) ", choices=['y', 'n'], default='y', show_choices=True) == "n":
            frames = get_call_stack()
            execute_search(frames[-4])

    if r_proc != None:
        console.print("[green]Result: ")
        console.print(r_proc)
