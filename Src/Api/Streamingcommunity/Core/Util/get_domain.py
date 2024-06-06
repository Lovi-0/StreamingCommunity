# 02.04.24

import os
import threading
import logging


# External library
import requests


# Internal utilities
from Src.Lib.Google import search as google_search



def check_url_for_content(url: str, content: str) -> bool:
    """
    Check if a URL contains specific content.

    Args:
        - url (str): The URL to check.
        - content (str): The content to search for in the response.

    Returns:
        bool: True if the content is found, False otherwise.
    """
    try:

        logging.info(f"Test site to extract domain: {url}")
        response = requests.get(url, timeout = 1)
        response.raise_for_status()

        if content in response.text:
            return True
        
    except Exception as e:
        pass

    return False


def grab_top_level_domain(base_url: str, target_content: str) -> str:
    """
    Get the top-level domain (TLD) from a list of URLs.

    Args:
        - base_url (str): The base URL to construct complete URLs.
        - target_content (str): The content to search for in the response.

    Returns:
        str: The found TLD, if any.
    """
    results = []
    threads = []
    path_file = os.path.join("Test", "data", "TLD", "tld_list.txt")
    logging.info(f"Load file: {path_file}")

    def url_checker(url: str):
        if check_url_for_content(url, target_content):
            results.append(url.split(".")[-1])

    if not os.path.exists(path_file):
        raise FileNotFoundError("The file 'tld_list.txt' does not exist.")

    with open(path_file, "r") as file:
        urls = [f"{base_url}.{x.strip().lower()}" for x in file]

    for url in urls:
        thread = threading.Thread(target=url_checker, args=(url,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if results:
        return results[-1]


def grab_top_level_domain_light(query: str) -> str:
    """
    Get the top-level domain (TLD) using a light method via Google search.

    Args:
        - query (str): The search query for Google search.
        
    Returns:
        str: The found TLD, if any.
    """
    for result in google_search(query, num=1, stop=1, pause=2):
        return result.split(".", 2)[-1].replace("/", "")


def grab_sc_top_level_domain(method: str) -> str:
    """
    Get the top-level domain (TLD) for the streaming community.
    Args:
        method (str): The method to use to obtain the TLD ("light" or "strong").
    Returns:
        str: The found TLD, if any.
    """
    if method == "light":
        return grab_top_level_domain_light("streaming community")
    elif method == "strong":
        return grab_top_level_domain("https://streamingcommunity", '<meta name="author" content="StreamingCommunity">')
