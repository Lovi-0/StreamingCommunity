# 13.09.2023

# General import
from Stream.util.console import console
import os, requests, time

# Variable
repo_name = "StreamingCommunity_api"
repo_user = "ghost6446"
main = os.path.abspath(os.path.dirname(__file__))
base = "\\".join(main.split("\\")[:-1])

def get_install_version():
    about = {}
    with open(os.path.join(main, '__version__.py'), 'r', encoding='utf-8') as f:
        exec(f.read(), about)
    return about['__version__']

def main_update():

    json = requests.get(f"https://api.github.com/repos/{repo_user}/{repo_name}/releases").json()[0]
    stargazers_count = requests.get(f"https://api.github.com/repos/{repo_user}/{repo_name}").json()['stargazers_count']
    last_version = json['name']
    down_count = json['assets'][0]['download_count']

    if down_count > 0 and stargazers_count > 0: percentual_stars = round(stargazers_count / down_count * 100, 2)
    else: percentual_stars = 0

    if get_install_version() != last_version: console.print(f"[red]=> A new version is available")
    else: console.print("[red]=> Everything up to date")
    
    print("\n")
    console.print(f"[red]{repo_name} was downloaded [yellow]{down_count} [red]times, but only [yellow]{percentual_stars}% [red]of You(!!) have starred it. \n\
        [cyan]Help the repository grow today, by leaving a [yellow]star [cyan]and [yellow]sharing [cyan]it to others online!")
    time.sleep(2.5)
    print("\n")