# 29.06.24

import tempfile
import logging


# External library
from bs4 import BeautifulSoup
from seleniumbase import Driver


# Internal utilities
from StreamingCommunity.Src.Util._jsonConfig import config_manager


# Config
USE_HEADLESS = config_manager.get_bool("BROWSER", "headless")


class WebAutomation:
    """
    A class for automating web interactions using SeleniumBase and BeautifulSoup.
    """

    def __init__(self):
        """
        Initializes the WebAutomation instance with SeleniumBase Driver.

        Parameters:
            headless (bool, optional): Whether to run the browser in headless mode. Default is True.
        """
        logging.getLogger('seleniumbase').setLevel(logging.ERROR)

        self.driver = Driver(
            uc=True, 
            uc_cdp_events=True, 
            headless=USE_HEADLESS,
            user_data_dir = tempfile.mkdtemp(),
            chromium_arg="--disable-search-engine-choice-screen"
        )
    
    def quit(self):
        """
        Quits the WebDriver instance.
        """
        self.driver.quit()
    
    def get_page(self, url):
        """
        Navigates the browser to the specified URL.

        Parameters:
            url (str): The URL to navigate to.
        """
        self.driver.get(url)
    
    def retrieve_soup(self):
        """
        Retrieves the BeautifulSoup object for the current page's HTML content.

        Returns:
            BeautifulSoup object: Parsed HTML content of the current page.
        """
        html_content = self.driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup
    
    def get_content(self):
        """
        Returns the HTML content of the current page.

        Returns:
            str: The HTML content of the current page.
        """
        return self.driver.page_source

