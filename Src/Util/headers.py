# 3.12.23 -> 10.12.23 -> 20.03.24

# Import
import fake_useragent

# Variable
useragent = fake_useragent.UserAgent(use_external_data=True)

def get_headers() -> str:
    """
    Generate a random user agent to use in HTTP requests.

    Returns:
    - str: A random user agent string.
    """
    
    # Get a random user agent string from the user agent rotator
    return useragent.firefox