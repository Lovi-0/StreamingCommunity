# 09.06.24

import os
import sys
import logging
from concurrent.futures import ThreadPoolExecutor


# External libraries
import httpx


# Internal utilities
from StreamingCommunity.Src.Util._jsonConfig import config_manager
from StreamingCommunity.Src.Util.headers import get_headers
from StreamingCommunity.Src.Util.os import os_manager


class ProxyManager:
    def __init__(self, proxy_list=None, url=None):
        """
        Initialize ProxyManager with a list of proxies and timeout.
        
        Parameters:
            - proxy_list: List of proxy strings
            - timeout: Timeout for proxy requests
        """
        self.proxy_list = proxy_list or []
        self.verified_proxies = []
        self.timeout = config_manager.get_float('REQUESTS', 'timeout')
        self.url = url

    def _check_proxy(self, proxy):
        """
        Check if a single proxy is working by making a request to Google.

        Parameters:
            - proxy: Proxy string to be checked

        Returns:
            - Proxy string if working, None otherwise
        """
        protocol = proxy.split(":")[0].lower()
        protocol = f'{protocol}://'
        proxy = {protocol: proxy, "https://": proxy}

        try:
            with httpx.Client(proxies=proxy, verify=False) as client:
                response = client.get(self.url, timeout=self.timeout, headers={'user-agent': get_headers()})

                if response.status_code == 200:
                    logging.info(f"Proxy {proxy} is working.")
                    return proxy
            
        except Exception as e:
            logging.error(f"Test proxy {proxy} failed: {e}")
            return None

    def verify_proxies(self):
        """
        Verify all proxies in the list and store the working ones.
        """
        logging.info("Starting proxy verification...")
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            self.verified_proxies = list(executor.map(self._check_proxy, self.proxy_list))
            
        self.verified_proxies = [proxy for proxy in self.verified_proxies if proxy]
        logging.info(f"Verification complete. {len(self.verified_proxies)} proxies are working.")

    def get_verified_proxies(self):
        """
        Get validate proxies.
        """

        if len(self.verified_proxies) > 0:
            return self.verified_proxies
        
        else:
            logging.error("Cant find valid proxy.")
            sys.exit(0)
        

def main_test_proxy(url_test):

    path_file_proxt_list = "list_proxy.txt"

    if os_manager.check_file(path_file_proxt_list):

        # Read file
        with open(path_file_proxt_list, 'r') as file:
            ip_addresses = file.readlines()

        # Formatt ip
        ip_addresses = [ip.strip() for ip in ip_addresses]
        formatted_ips = [f"http://{ip}" for ip in ip_addresses]

    # Get list of proxy from config.json
    proxy_list = formatted_ips

    # Verify proxy
    manager = ProxyManager(proxy_list, url_test)
    manager.verify_proxies()

    # Write valid ip in txt file
    with open(path_file_proxt_list, 'w') as file:
        for ip in ip_addresses:
            file.write(f"{ip}\n")
    
    # Return valid proxy
    return manager.get_verified_proxies()
