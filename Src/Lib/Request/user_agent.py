# 04.4.24

import logging
import re
import os
import random
import threading
import json
import tempfile
from typing import Dict, List

# Internal utilities
from .my_requests import request


def get_browser_user_agents_online(browser: str) -> List[str]:
    """
    Retrieve browser user agent strings from a website.

    Args:
        browser (str): The name of the browser (e.g., 'chrome', 'firefox', 'safari').

    Returns:
        List[str]: List of user agent strings for the specified browser.
    """
    url = f"https://useragentstring.com/pages/{browser}/"

    try:

        # Make request and find all user agents
        html = request.get(url).text
        browser_user_agents = re.findall(r"<a href=\'/.*?>(.+?)</a>", html, re.UNICODE)
        return [ua for ua in browser_user_agents if "more" not in ua.lower()]
    
    except Exception as e:
        logging.error(f"Failed to fetch user agents for '{browser}': {str(e)}")
        return []


def update_user_agents(browser_name: str, browser_user_agents: Dict[str, List[str]]) -> None:
    """
    Update browser user agents dictionary with new requests.

    Args:
        browser_name (str): Name of the browser.
        browser_user_agents (Dict[str, List[str]]): Dictionary to store browser user agents.
    """
    browser_user_agents[browser_name] = get_browser_user_agents_online(browser_name)


def create_or_update_user_agent_file() -> None:
    """
    Create or update the user agent file with browser user agents.
    """
    user_agent_file = os.path.join(os.environ.get('TEMP'), 'fake_user_agent.json')
    
    if not os.path.exists(user_agent_file):
        browser_user_agents: Dict[str, List[str]] = {}
        threads = []

        for browser_name in ['chrome', 'firefox', 'safari']:
            t = threading.Thread(target=update_user_agents, args=(browser_name, browser_user_agents))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        with open(user_agent_file, 'w') as f:
            json.dump(browser_user_agents, f, indent=4)
            logging.info(f"User agent file created at: {user_agent_file}")
            
    else:
        logging.info("User agent file already exists.")


class UserAgentManager:
    """
    Manager class to access browser user agents from a file.
    """
    def __init__(self):

        # Get path to temp file where save all user agents
        self.user_agent_file = os.path.join(tempfile.gettempdir(), 'fake_user_agent.json')

        # If file dont exist, creaet it
        if not os.path.exists(self.user_agent_file):
            create_or_update_user_agent_file()

    def get_random_user_agent(self, browser: str) -> str:
        """
        Get a random user agent for the specified browser.

        Args:
            browser (str): The name of the browser ('chrome', 'firefox', 'safari').

        Returns:
            Optional[str]: Random user agent string for the specified browser.
        """
        with open(self.user_agent_file, 'r') as f:
            browser_user_agents = json.load(f)
            return random.choice(browser_user_agents.get(browser.lower(), []))


# Output
ua = UserAgentManager()