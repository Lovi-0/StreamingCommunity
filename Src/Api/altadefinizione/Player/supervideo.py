# 26.05.24

import re
import sys
import logging


# External libraries
import httpx
import jsbeautifier
from bs4 import BeautifulSoup


# Internal utilities
from Src.Util.headers import get_headers


class VideoSource:
    def __init__(self, url: str):
        """
        Sets up the video source with the provided URL.

        Parameters:
            - url (str): The URL of the video.
        """
        self.url = url
        self.headers = {'user-agent': get_headers()}

    def setup(self, url: str) -> None:
        """
        Sets up the video source with the provided URL.

        Parameters:
            - url (str): The URL of the video source.
        """
        self.url = url

    def make_request(self, url: str) -> str:
        """
        Make an HTTP GET request to the provided URL.

        Parameters:
            - url (str): The URL to make the request to.

        Returns:
            - str: The response content if successful, None otherwise.
        """

        try:
            response = httpx.get(url, headers=self.headers, follow_redirects=True)
            response.raise_for_status()

            return response.text
        
        except Exception as e:
            logging.error(f"Request failed [supervideo]: {e}")
            return None

    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse the provided HTML content using BeautifulSoup.

        Parameters:
            - html_content (str): The HTML content to parse.

        Returns:
            - BeautifulSoup: Parsed HTML content if successful, None otherwise.
        """

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            return soup
        
        except Exception as e:
            logging.error(f"Failed to parse HTML content: {e}")
            return None
        
    def get_iframe(self, soup):
        """
        Extracts the source URL of the second iframe in the provided BeautifulSoup object.

        Parameters:
            - soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML.

        Returns:
            - str: The source URL of the second iframe, or None if not found.
        """
        iframes = soup.find_all("iframe")
        if iframes and len(iframes) > 1:
            return iframes[1].get("src")
        
        return None

    def find_content(self, url):
        """
        Makes a request to the specified URL and parses the HTML content.

        Parameters:
            - url (str): The URL to fetch content from.

        Returns:
            - BeautifulSoup: A BeautifulSoup object representing the parsed HTML content, or None if the request fails.
        """
        content = self.make_request(url)
        if content:
            return self.parse_html(content)
        
        return None

    def get_result_node_js(self, soup):
        """
        Prepares and runs a Node.js script from the provided BeautifulSoup object to retrieve the video URL.

        Parameters:
            - soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML content.

        Returns:
            - str: The output from the Node.js script, or None if the script cannot be found or executed.
        """
        for script in soup.find_all("script"):
            if "eval" in str(script):
                return jsbeautifier.beautify(script.text)
            
        return None

    def get_playlist(self) -> str:
        """
        Download a video from the provided URL.

        Returns:
            - str: The URL of the downloaded video if successful, None otherwise.
        """
        try:
            html_content = self.make_request(self.url)
            if not html_content:
                logging.error("Failed to fetch HTML content.")
                return None

            soup = self.parse_html(html_content)
            if not soup:
                logging.error("Failed to parse HTML content.")
                return None

            iframe_src = self.get_iframe(soup)
            if not iframe_src:
                logging.error("No iframe found.")
                return None

            down_page_soup = self.find_content(iframe_src)
            if not down_page_soup:
                logging.error("Failed to fetch down page content.")
                return None

            pattern = r'data-link="(//supervideo[^"]+)"'
            match = re.search(pattern, str(down_page_soup))
            if not match:
                logging.error("No player available for download.")
                return None

            supervideo_url = "https:" + match.group(1)
            supervideo_soup = self.find_content(supervideo_url)
            if not supervideo_soup:
                logging.error("Failed to fetch supervideo content.")
                return None

            # Find master playlist
            data_js = self.get_result_node_js(supervideo_soup)

            match = re.search(r'sources:\s*\[\{\s*file:\s*"([^"]+)"', data_js)
            if match:
                return match.group(1)
            
            return None

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None
        
