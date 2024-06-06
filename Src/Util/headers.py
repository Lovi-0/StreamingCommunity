# 4.04.24

import logging


# External library
import fake_useragent


# Variable
useragent = fake_useragent.UserAgent()


def get_headers() -> str:
    """
    Generate a random user agent to use in HTTP requests.

    Returns:
        - str: A random user agent string.
    """
    
    # Get a random user agent string from the user agent rotator
    return useragent.firefox