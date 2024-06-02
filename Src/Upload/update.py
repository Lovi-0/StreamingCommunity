# 01.03.2023

import os
import time


# Internal utilities
from .version import __version__
from Src.Util.console import console


# External library
from Src.Lib.Request import requests


# Variable
repo_name = "StreamingCommunity_api"
repo_user = "ghost6446"
main = os.path.abspath(os.path.dirname(__file__))


def update():
    """
    Check for updates on GitHub and display relevant information.
    """

    console.print("[green]Checking GitHub version [white]...")

    # Make the GitHub API requests and handle potential errors
    try:
        response_reposity = requests.get(f"https://api.github.com/repos/{repo_user}/{repo_name}").json()
        response_releases = requests.get(f"https://api.github.com/repos/{repo_user}/{repo_name}/releases").json()
    except requests.RequestException as e:
        console.print(f"[red]Error accessing GitHub API: {e}")
        return

    # Get stargazers count from the repository
    stargazers_count = response_reposity.get('stargazers_count', 0)

    # Calculate total download count from all releases
    total_download_count = sum(asset['download_count'] for release in response_releases for asset in release.get('assets', []))

    # Get latest version name
    if response_releases:
        last_version = response_releases[0].get('name', 'Unknown')
    else:
        last_version = 'Unknown'

    # Calculate percentual of stars based on download count
    if total_download_count > 0 and stargazers_count > 0:
        percentual_stars = round(stargazers_count / total_download_count * 100, 2)
    else:
        percentual_stars = 0

    # Check installed version
    if __version__ != last_version:
        console.print(f"[red]New version available: [yellow]{last_version}")
    else:
        console.print(f"[red]Everything is up to date")

    console.print("\n")
    console.print(f"[red]{repo_name} has been downloaded [yellow]{total_download_count} [red]times, but only [yellow]{percentual_stars}% [red]of users have starred it.\n\
        [cyan]Help the repository grow today by leaving a [yellow]star [cyan]and [yellow]sharing [cyan]it with others online!")
    
    console.print("\n")
