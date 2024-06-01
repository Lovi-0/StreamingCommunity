# 13.05.24

import socket
import logging
import urllib3
from urllib.parse import urlparse, urlunparse


import warnings
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)


# Variable
url_test = "https://sc-b1-18.scws-content.net/hls/170/3/25/32503b5b-4646-4376-ad47-7766c65be7e2/audio/ita/0004-0100.ts"


def get_ip_from_url(url):
    """
    Extracts the IP address from a given URL.

    Args:
        url (str): The URL from which to extract the IP address.

    Returns:
        str or None: The extracted IP address if successful, otherwise None.
    """
    try:
        parsed_url = urlparse(url)
        if not parsed_url.hostname:
            logging.error(f"Invalid URL: {url}")
            return None
        
        ip_address = socket.gethostbyname(parsed_url.hostname)
        return ip_address
    
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

def replace_random_number(url, random_number):
    """
    Replaces a random number in the URL.

    Args:
        url (str): The URL in which to replace the random number.
        random_number (int): The random number to replace in the URL.

    Returns:
        str: The modified URL with the random number replaced.
    """
    parsed_url = urlparse(url)
    parts = parsed_url.netloc.split('.')
    prefix = None

    for i, part in enumerate(parts):
        if '-' in part and part.startswith("sc-"):
            prefix = part.split('-')[0] + '-' + part.split('-')[1] + '-'
            new_part = prefix + f"{random_number:02d}"
            parts[i] = new_part
            break

    new_netloc = '.'.join(parts)
    return urlunparse((parsed_url.scheme, new_netloc, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))

def main():
    """
    Main function to test the URL manipulation.
    """
    valid_ip = []

    for i in range(1, 36):
        try:
            ip = get_ip_from_url(replace_random_number(url_test, i))

            if ip:
                valid_ip.append(ip)

        except Exception as e:
            logging.error(f"Error: {e}")
            pass

    print(f"Valid IP addresses: {sorted(valid_ip, reverse=True)}")

if __name__ == '__main__':
    main()
