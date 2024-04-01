# 01.03.2023

# Class import
from Src.Util.console import console

# General import
import os
import requests
import time

# Variable
repo_name = "StreamingCommunity_api"
repo_user = "ghost6446"
main = os.path.abspath(os.path.dirname(__file__))


def get_install_version():
    """
    Get the installed version from the '__version__.py' file.
    """

    about = {}

    version_file_path = os.path.join(main, '__version__.py')
    
    with open(version_file_path, 'r', encoding='utf-8') as f:
        exec(f.read(), about)

    return about['__version__']

def update():
    """
    Check for updates on GitHub and display relevant information.
    """

    console.print("[green]Checking GitHub version [white]...")

    # Make the GitHub API requests and handle potential errors
    try:
        repo_info = requests.get(f"https://api.github.com/repos/{repo_user}/{repo_name}").json()
        release_info = requests.get(f"https://api.github.com/repos/{repo_user}/{repo_name}/releases").json()[0]
    except requests.RequestException as e:
        console.print(f"[red]Error accessing GitHub API: {e}")
        return

    # Get start of the reposity
    stargazers_count = repo_info['stargazers_count']

    # Find info about latest versione deploy and the donwload count 
    last_version = release_info['name']
    down_count = release_info['assets'][0]['download_count']

    # Calculate percentual of start base on download count
    if down_count > 0 and stargazers_count > 0:
        percentual_stars = round(stargazers_count / down_count * 100, 2)
    else:
        percentual_stars = 0

    installed_version = get_install_version()

    # Check installed version
    if installed_version != last_version:
        console.print(f"[red]Version: [yellow]{last_version}")
    else:
        console.print(f"[red]Everything up to date")

    print("\n")
    console.print(f"[red]{repo_name} was downloaded [yellow]{down_count} [red]times, but only [yellow]{percentual_stars}% [red]of You(!!) have starred it.\n\
        [cyan]Help the repository grow today, by leaving a [yellow]star [cyan]and [yellow]sharing [cyan]it to others online!")
    
    time.sleep(3)
    print("\n")

