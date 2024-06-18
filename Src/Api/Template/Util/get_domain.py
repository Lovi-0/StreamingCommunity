# 18.06.24

import os
import sys
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


# External libraries
import httpx
import psutil
from tqdm import tqdm


# Internal utilities
from Src.Util.color import Colors
from Src.Util.headers import get_headers
from Src.Util.console import console
from Src.Util._jsonConfig import config_manager



def check_url_for_content(url: str, content: str, timeout: int = 1) -> bool:
    """
    Check if a URL contains specific content.

    Args:
        - url (str): The URL to check.
        - content (str): The content to search for in the response.
        - timeout (int): Timeout for the request in seconds.

    Returns:
        bool: True if the content is found, False otherwise.
    """
    try:

        response = httpx.get(url, timeout=timeout, headers={'user-agent': get_headers()})
        logging.info(f"Testing site to extract domain: {url}, response: {response.status_code}")

        # Raise an error if the status is not successful
        response.raise_for_status()

        # Check if the target content is in the response text
        if content in response.text:
            return True
        
    except httpx.RequestError as e:
        logging.warning(f"Request error for {url}: {e}")

    except httpx.HTTPStatusError as e:
        logging.warning(f"HTTP status error for {url}: {e}")

    except Exception as e:
        logging.warning(f"Error for {url}: {e}")

    return False

def get_top_level_domain(base_url: str, target_content: str, max_workers: int = os.cpu_count(), timeout: int = 2, retries: int = 1) -> str:
    """
    Get the top-level domain (TLD) from a list of URLs.

    Args:
        - base_url (str): The base URL to construct complete URLs.
        - target_content (str): The content to search for in the response.
        - max_workers (int): Maximum number of threads.
        - timeout (int): Timeout for the request in seconds.
        - retries (int): Number of retries for failed requests.

    Returns:
        str: The found TLD, if any.
    """

    results = []
    failed_urls = []
    path_file = os.path.join("Test", "data", "TLD", "tld_list_complete.txt")
    logging.info(f"Loading file: {path_file}")

    if not os.path.exists(path_file):
        raise FileNotFoundError("The file 'tld_list_complete.txt' does not exist.")

    # Read TLDs from file and create URLs to test
    with open(path_file, "r") as file:
        urls = [f"{base_url}.{x.strip().lower()}" for x in file]
    urls = list(set(urls))  # Remove duplicates

    start_time = time.time()

    bar_format=f"{Colors.YELLOW}Testing URLS{Colors.WHITE}: {Colors.RED}{{percentage:.2f}}% {Colors.MAGENTA}{{bar}} {Colors.WHITE}[ {Colors.YELLOW}{{n_fmt}}{Colors.WHITE} / {Colors.RED}{{total_fmt}} {Colors.WHITE}] {Colors.YELLOW}{{elapsed}} {Colors.WHITE}< {Colors.CYAN}{{remaining}}{Colors.GREEN}{{postfix}} {Colors.WHITE}]"
    progress_bar = tqdm(
        total=len(urls), 
        unit='url',
        ascii='░▒█',
        bar_format=bar_format
    )

    # Event to signal when to stop checking URLs
    stop_event = threading.Event()

    def url_checker(url: str):
        for attempt in range(retries):
            if stop_event.is_set():
                return None
            
            if check_url_for_content(url, target_content, timeout):
                stop_event.set()
                progress_bar.update(1)
                return url.split(".")[-1]
            
            logging.info(f"Retrying {url} ({attempt+1}/{retries})")

        failed_urls.append(url)
        progress_bar.update(1)
        return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(url_checker, url): url for url in urls}

        for future in as_completed(futures):
            tld = future.result()

            if tld:
                results.append(tld)
                if stop_event.is_set():
                    break

            # Update the progress bar with CPU usage info
            progress_bar.set_postfix(cpu_usage=f"{psutil.cpu_percent()}%")

    progress_bar.close()

    end_time = time.time()
    total_time = end_time - start_time
    avg_time_per_url = total_time / len(urls) if urls else 0

    logging.info(f"Tested {len(urls)} URLs: {len(results)} passed, {len(failed_urls)} failed.")
    logging.info(f"Total time: {total_time:.2f} seconds, Average time per URL: {avg_time_per_url:.2f} seconds.")

    if results:
        return results[-1]
    else:
        return None
    

def search_domain(site_name: str, target_content: str, base_url: str):
    """
    Search for a valid domain for the given site name and base URL.

    Args:
        - site_name (str): The name of the site to search the domain for.
        - target_content (str): The content to search for in the response.
        - base_url (str): The base URL to construct complete URLs.

    Returns:
        tuple: The found domain and the complete URL.
    """

    # Extract config domain
    domain = config_manager.get("SITE", site_name)
    console.print(f"[cyan]Test site[white]: [red]{base_url}.{domain}")

    try:
        # Test the current domain
        response = httpx.get(f"{base_url}.{domain}", headers={'user-agent': get_headers()}, timeout=2)
        console.print(f"[cyan]Test response site[white]: [red]{response.status_code}")
        response.raise_for_status()

        # Return config domain
        console.print(f"[cyan]Use domain: [red]{domain}")
        return domain, f"{base_url}.{domain}"

    except:

        # If the current domain fails, find a new one
        print()
        console.print("[red]Extract new DOMAIN from TLD list.")
        new_domain = get_top_level_domain(base_url=base_url, target_content=target_content)

        if new_domain is not None:

            # Update domain in config.json
            config_manager.set_key('SITE', site_name, new_domain)
            config_manager.write_config()

            # Return new config domain
            console.print(f"[cyan]Use domain: [red]{new_domain}")
            return new_domain, f"{base_url}.{new_domain}"
        
        else:
            logging.error(f"Failed to find a new domain for: {base_url}")
            sys.exit(0)
