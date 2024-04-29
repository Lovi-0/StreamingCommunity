# 29.04.24

import time
import ssl
from urllib.request import Request, urlopen
from urllib.parse import quote_plus, urlparse, parse_qs
from bs4 import BeautifulSoup

from typing import Generator, Optional


# Internal utilities
from Src.Lib.Request import requests



def get_page(url: str) -> bytes:
    """
    Fetches the HTML content of a webpage given its URL.

    Args:
        url (str): The URL of the webpage.

    Returns:
        bytes: The HTML content of the webpage.
    """

    response = requests.get(url)
    return response.text


def filter_result(link: str) -> Optional[str]:
    """
    Filters search result links to remove unwanted ones.

    Args:
        link (str): The URL of the search result.

    Returns:
        Optional[str]: The filtered URL if valid, None otherwise.
    """
    try:
        if link.startswith('/url?'):

            # Extract the actual URL from Google's redirect link
            o = urlparse(link, 'http')
            link = parse_qs(o.query)['q'][0]

        o = urlparse(link, 'http')

        # Filter out Google links
        if o.netloc and 'google' not in o.netloc:
            return link
        
    except Exception:
        pass


def search(query: str, num: int = 10, stop: Optional[int] = None, pause: float = 2.0) -> Generator[str, None, None]:
    """
    Performs a Google search and yields the URLs of search results.

    Args:
        query (str): The search query.
        num (int): Number of results to fetch per request. Default is 10.
        stop (int, optional): Total number of results to retrieve. Default is None.
        pause (float): Pause duration between requests. Default is 2.0.

    Yields:
        str: The URL of a search result.
        
    Example:
        >>> for url in search("Python tutorials", num=5, stop=10):
        ...     print(url)
        ...
        https://www.python.org/about/gettingstarted/
    """

    # Set to store unique URLs
    hashes = set()

    # Counter for the number of fetched URLs
    count = 0

    # Encode the query for URL
    query = quote_plus(query)

    while not stop or count < stop:
        last_count = count

        # Construct the Google search URL
        url = f"https://www.google.com/search?client=opera&q={query}&sourceid=opera&oe=UTF-8"

        # Pause before making the request
        time.sleep(pause)
        
        # Fetch the HTML content of the search page
        html = get_page(url)
        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Find all anchor tags containing search result links
            anchors = soup.find(id='search').findAll('a')
        except AttributeError:
            # Handle cases where search results are not found in the usual div
            gbar = soup.find(id='gbar')
            if gbar:
                gbar.clear()
            anchors = soup.findAll('a')

        # Iterate over each anchor tag
        for a in anchors:
            try:
                link = a['href']
            except KeyError:
                continue

            # Filter out unwanted links
            link = filter_result(link)
            if not link:
                continue

            # Check for duplicate URLs
            h = hash(link)
            if h in hashes:
                continue
            hashes.add(h)

            # Yield the valid URL
            yield link

            # Increment the counter
            count += 1
            # Check if the desired number of URLs is reached
            if stop and count >= stop:
                return

        # Break the loop if no new URLs are found
        if last_count == count:
            break
