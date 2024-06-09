# 09.06.24

import time
import logging
from concurrent.futures import ThreadPoolExecutor


# External libraries
import requests


# Internal utilities
from Src.Util._jsonConfig import config_manager


class ProxyManager:
    def __init__(self, proxy_list=None, url=None):
        """
        Initialize ProxyManager with a list of proxies and timeout.
        
        Args:
            - proxy_list: List of proxy strings
            - timeout: Timeout for proxy requests
        """
        self.proxy_list = proxy_list or []
        self.verified_proxies = []
        self.failed_proxies = {}
        self.timeout = config_manager.get_float('REQUESTS', 'timeout')
        self.url = url

    def _check_proxy(self, proxy):
        """
        Check if a single proxy is working by making a request to Google.

        Args:
            - proxy: Proxy string to be checked

        Returns:
            - Proxy string if working, None otherwise
        """
        protocol = proxy.split(":")[0].lower()

        try:
            response = requests.get(self.url, proxies={protocol: proxy}, timeout=self.timeout)

            if response.status_code == 200:
                logging.info(f"Proxy {proxy} is working.")
                return proxy
            
        except requests.RequestException as e:
            logging.error(f"Proxy {proxy} failed: {e}")
            self.failed_proxies[proxy] = time.time()
            return None

    def verify_proxies(self):
        """
        Verify all proxies in the list and store the working ones.
        """
        logging.info("Starting proxy verification...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            self.verified_proxies = list(executor.map(self._check_proxy, self.proxy_list))
        self.verified_proxies = [proxy for proxy in self.verified_proxies if proxy]
        logging.info(f"Verification complete. {len(self.verified_proxies)} proxies are working.")

    def get_verified_proxies(self):
        """
        Get validate proxies.
        """
        validate_proxy = []

        for proxy in self.verified_proxies:
            protocol = proxy.split(":")[0].lower()
            validate_proxy.append({protocol: proxy})

        return validate_proxy
    

def main_test_proxy(url_test):

    # Get list of proxy from config.json
    proxy_list = config_manager.get_list('REQUESTS', 'proxy')

    # Verify proxy
    manager = ProxyManager(proxy_list, url_test)
    manager.verify_proxies()
    
    # Return valid proxy
    return manager.get_verified_proxies()
