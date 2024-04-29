# 29.04.24

import threading
import logging
import os


# Internal utilities
from Src.Lib.Google import search as google_search
from Src.Lib.Request import requests


def check_url_for_content(url: str, content: str) -> bool:
    """
    Check if a URL contains specific content.

    Args:
        url (str): The URL to check.
        content (str): The content to search for in the response.

    Returns:
        bool: True if the content is found, False otherwise.
    """
    try:
        r = requests.get(url, timeout = 1)
        if r.status_code == 200 and content in r.text:
            return True
    except Exception as e:
        pass
    return False

def grab_top_level_domain(base_url: str, target_content: str) -> str:
    """
    Get the top-level domain (TLD) from a list of URLs.

    Args:
        base_url (str): The base URL to construct complete URLs.
        target_content (str): The content to search for in the response.

    Returns:
        str: The found TLD, if any.
    """
    results = []
    threads = []

    def url_checker(url: str):
        if check_url_for_content(url, target_content):
            results.append(url.split(".")[-1])

    if not os.path.exists("tld_list.txt"):
        raise FileNotFoundError("The file 'tld_list.txt' does not exist.")

    urls = [f"{base_url}.{x.strip().lower()}" for x in open("tld_list.txt", "r")]

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
        query (str): The search query for Google search.

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

def grab_au_top_level_domain(method: str) -> str:
    """
    Get the top-level domain (TLD) for Anime Unity.

    Args:
        method (str): The method to use to obtain the TLD ("light" or "strong").

    Returns:
        str: The found TLD, if any.
    """
    if method == "light":
        return grab_top_level_domain_light("animeunity")
    elif method == "strong":
        return grab_top_level_domain("https://www.animeunity", '<meta name="author" content="AnimeUnity Staff">')

def compose_both_top_level_domains(method: str) -> dict:
    """
    Compose TLDs for both the streaming community and Anime Unity.

    Args:
        method (str): The method to use to obtain the TLD ("light" or "strong").

    Returns:
        dict: A dictionary containing the TLDs for the streaming community and Anime Unity.
    """
    sc_tld = grab_sc_top_level_domain(method)
    au_tld = grab_au_top_level_domain(method)

    if not sc_tld:
        sc_tld = grab_sc_top_level_domain("strong")

    if not au_tld:
        au_tld = grab_au_top_level_domain("strong")

    return {"streaming_community": sc_tld, "anime_unity": au_tld}