# 4.04.24

import logging


# Internal utilities
from Src.Lib.UserAgent import ua


def get_headers() -> str:
    """
    Generate a random user agent to use in HTTP requests.

    Returns:
    - str: A random user agent string.
    """
    
    # Get a random user agent string from the user agent rotator
    random_headers = ua.get_random_user_agent("firefox")

    #logging.info(f"Use headers: {random_headers}")
    return random_headers