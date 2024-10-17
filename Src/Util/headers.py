# 4.04.24

import re
import random


# External library
from fake_useragent import UserAgent


# Variable
ua = UserAgent()


def extract_versions(user_agent):
    """
    Extract browser versions from the user agent.

    Parameters:
        user_agent (str): User agent of the browser.

    Returns:
        list: List of browser versions.
    """

    # Patterns to extract versions from various user agents
    patterns = {
        'chrome': re.compile(r'Chrome/(\d+)\.(\d+)\.(\d+)\.(\d+)'),
        'firefox': re.compile(r'Firefox/(\d+)\.?(\d+)?\.?(\d+)?'),
        'safari': re.compile(r'Version/(\d+)\.(\d+)\.(\d+) Safari/(\d+)\.(\d+)\.(\d+)'),
        'edge': re.compile(r'Edg/(\d+)\.(\d+)\.(\d+)\.(\d+)'),
        'edgios': re.compile(r'EdgiOS/(\d+)\.(\d+)\.(\d+)\.(\d+)'),
        'crios': re.compile(r'CriOS/(\d+)\.(\d+)\.(\d+)\.(\d+)'),
    }

    for key, pattern in patterns.items():
        match = pattern.search(user_agent)
        if match:
            return [match.group(i+1) for i in range(match.lastindex)]

    # Fallback values if specific versions are not found
    return ['99', '0', '0', '0']

def get_platform(user_agent):
    """
    Determine the device platform from the user agent.

    Parameters:
        user_agent (str): User agent of the browser.

    Returns:
        str: Device platform.
    """
    if 'Windows' in user_agent:
        return '"Windows"'
    elif 'Mac OS X' in user_agent:
        return '"macOS"'
    elif 'Android' in user_agent:
        return '"Android"'
    elif 'iPhone' in user_agent or 'iPad' in user_agent:
        return '"iOS"'
    elif 'Linux' in user_agent:
        return '"Linux"'
    return '"Unknown"'

def get_model(user_agent):
    """
    Determine the device model from the user agent.

    Parameters:
        user_agent (str): User agent of the browser.

    Returns:
        str: Device model.
    """
    if 'iPhone' in user_agent:
        return '"iPhone"'
    elif 'iPad' in user_agent:
        return '"iPad"'
    elif 'Android' in user_agent:
        return '"Android"'
    elif 'Windows' in user_agent:
        return '"PC"'
    elif 'Mac OS X' in user_agent:
        return '"Mac"'
    elif 'Linux' in user_agent:
        return '"Linux"'
    return '"Unknown"'

def random_headers(referer: str = None):
    """
    Generate random HTTP headers to simulate human-like behavior.

    Returns:
        dict: Generated HTTP headers.
    """
    user_agent = ua.random
    versions = extract_versions(user_agent)
    platform = get_platform(user_agent)
    model = get_model(user_agent)
    is_mobile = 'Mobi' in user_agent or 'Android' in user_agent

    # Generate sec-ch-ua string based on the browser
    if 'Chrome' in user_agent or 'CriOS' in user_agent:
        sec_ch_ua = f'" Not;A Brand";v="{versions[0]}", "Chromium";v="{versions[0]}", "Google Chrome";v="{versions[0]}"'
    elif 'Edg' in user_agent or 'EdgiOS' in user_agent:
        sec_ch_ua = f'" Not;A Brand";v="{versions[0]}", "Chromium";v="{versions[0]}", "Microsoft Edge";v="{versions[0]}"'
    elif 'Firefox' in user_agent:
        sec_ch_ua = f'" Not;A Brand";v="{versions[0]}", "Firefox";v="{versions[0]}"'
    elif 'Safari' in user_agent:
        sec_ch_ua = f'" Not;A Brand";v="{versions[0]}", "Safari";v="{versions[0]}"'
    else:
        sec_ch_ua = f'" Not;A Brand";v="{versions[0]}"'

    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(['en-US', 'en-GB', 'fr-FR', 'es-ES', 'de-DE']),
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua-mobile': '?1' if is_mobile else '?0',
        'sec-ch-ua-platform': platform,
        'sec-ch-ua': sec_ch_ua,
        'sec-ch-ua-model': model
    }

    if referer:
        headers['Origin'] = referer
        headers['Referer'] = referer
    
    return headers

def get_headers() -> str:
    """
    Generate a random user agent to use in HTTP requests.

    Returns:
        - str: A random user agent string.
    """
    
    # Get a random user agent string from the user agent rotator
    return str(ua.chrome)
