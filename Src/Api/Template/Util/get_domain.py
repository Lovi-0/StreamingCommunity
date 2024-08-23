# 18.06.24

import os
import sys
import time
import logging
from urllib.parse import urlparse


# External libraries
import httpx


# Internal utilities
from Src.Util.headers import get_headers
from Src.Util.console import console
from Src.Util._jsonConfig import config_manager



def search_domain(site_name: str, base_url: str):
    """
    Search for a valid domain for the given site name and base URL.

    Parameters:
        - site_name (str): The name of the site to search the domain for.
        - base_url (str): The base URL to construct complete URLs.
        - follow_redirects (bool): To follow redirect url or not.

    Returns:
        tuple: The found domain and the complete URL.
    """

    # Extract config domain
    domain = str(config_manager.get_dict("SITE", site_name)['domain'])
    console.print(f"[cyan]Test site[white]: [red]{base_url}.{domain}")

    # Test the current domain
    response_follow = httpx.get(f"{base_url}.{domain}", headers={'user-agent': get_headers()}, timeout=5, follow_redirects=True)
    #console.print(f"[cyan]Test response site[white]: [red]{response_follow.status_code}")
    response_follow.raise_for_status()

    # Ensure the URL is in string format before parsing
    parsed_url = urlparse(str(response_follow.url))
    parse_domain = parsed_url.netloc
    tld = parse_domain.split('.')[-1]

    if tld is not None:
        
        # Update domain in config.json
        config_manager.config['SITE'][site_name]['domain'] = tld
        config_manager.write_config()

    # Return config domain
    console.print(f"[cyan]Use domain: [red]{tld} \n")
    return tld, f"{base_url}.{tld}"
