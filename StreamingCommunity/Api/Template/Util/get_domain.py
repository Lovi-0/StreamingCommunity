# 18.06.24

import sys
from urllib.parse import urlparse


# External libraries
import httpx
from googlesearch import search


# Internal utilities
from StreamingCommunity.Util.headers import get_headers
from StreamingCommunity.Util.console import console, msg
from StreamingCommunity.Util._jsonConfig import config_manager


def google_search(query):
    """
    Perform a Google search and return the first result.
    
    Args:
        query (str): Search query to execute
        
    Returns:
        str: First URL from search results, None if no results found
    """

    # Perform search with single result limit
    search_results = search(query, num_results=1)
    first_result = next(search_results, None)
    
    if not first_result:
        console.print("[red]No results found.[/red]")
    
    return first_result

def validate_url(url, max_timeout):
    """
    Validate if a URL is accessible and check if its redirect destination is significantly different.
    
    Args:
        url (str): URL to validate
        max_timeout (int): Maximum timeout for request
        
    Returns:
        bool: True if URL is valid, accessible and redirect destination is acceptable
    """
    def get_domain_parts(url_str):
        parsed = urlparse(url_str)
        return parsed.netloc.lower().split('.')[-2:]  # Get last two parts of domain
    
    try:
        # First check without following redirects
        with httpx.Client(
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent': get_headers()
            },
            follow_redirects=False,
            timeout=max_timeout
        ) as client:
            response = client.get(url)
            if response.status_code == 403:
                return False
            response.raise_for_status()
            
        # Then check with redirects enabled
        with httpx.Client(
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent': get_headers()
            },
            follow_redirects=True,
            timeout=max_timeout
        ) as client:
            response = client.get(url)
            if response.status_code == 403:
                return False
            response.raise_for_status()
            
            # Compare original and final URLs
            original_domain = get_domain_parts(url)
            final_domain = get_domain_parts(str(response.url))
            
            # Check if domains are significantly different
            if original_domain != final_domain:
                console.print(f"[yellow]Warning: URL redirects to different domain: {response.url}[/yellow]")
                return False
                
            return True
            
    except Exception:
        return False
    
def get_final_redirect_url(initial_url, max_timeout):
    """
    Follow all redirects for a URL and return final destination.
    
    Args:
        initial_url (str): Starting URL to follow redirects from
        max_timeout (int): Maximum timeout for request
        
    Returns:
        str: Final URL after all redirects, None if error occurs
    """
    try:
        with httpx.Client(
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent': get_headers()
            },
            follow_redirects=True,
            timeout=max_timeout
        ) as client:
            
            # Follow redirects and get response
            response = client.get(initial_url)

            if response.status_code == 403:
                console.print("[bold red]The owner of this website has banned your IP[/bold red]")
                raise

            response.raise_for_status()
            return response.url
    
    except Exception as e:
        console.print(f"\n[cyan]Test url[white]: [red]{initial_url}, [cyan]error[white]: [red]{e}")
        return None

def search_domain(site_name: str, base_url: str, get_first: bool = False):
    """
    Search for valid domain matching site name and base URL.
    
    Args:
        site_name (str): Name of site to find domain for
        base_url (str): Base URL to construct complete URLs
        get_first (bool): Auto-update config with first valid match if True
        
    Returns:
        tuple: (found_domain, complete_url)
    """
    # Get configuration values
    max_timeout = config_manager.get_int("REQUESTS", "timeout")
    domain = str(config_manager.get_dict("SITE", site_name)['domain'])
    test_url = f"{base_url}.{domain}"

    try:
        if validate_url(test_url, max_timeout):
            parsed_url = urlparse(test_url)
            tld = parsed_url.netloc.split('.')[-1]
            config_manager.config['SITE'][site_name]['domain'] = tld
            config_manager.write_config()
            return tld, test_url

    except Exception:
        pass

    # Perform Google search if current domain fails
    query = base_url.split("/")[-1]
    search_results = list(search(query, num_results=15, lang="it"))
    console.print(f"Google search: {search_results}")

    def normalize_for_comparison(url):
        """Normalize URL by removing protocol, www, and trailing slashes"""
        url = url.lower()
        url = url.replace("https://", "").replace("http://", "")
        url = url.replace("www.", "")
        return url.rstrip("/")

    target_url = normalize_for_comparison(base_url)

    # Check each search result
    for result_url in search_results:
        #console.print(f"[green]Checking url[white]: [red]{result_url}")

        # Skip invalid URLs
        if not validate_url(result_url, max_timeout):
            #console.print(f"[red]URL validation failed for: {result_url}")
            continue

        parsed_result = urlparse(result_url)
        result_domain = normalize_for_comparison(parsed_result.netloc)

        # Check if domain matches target
        if result_domain.startswith(target_url.split("/")[-1]):
            final_url = get_final_redirect_url(result_url, max_timeout)
            
            if final_url is not None:
                new_domain = urlparse(str(final_url)).netloc.split(".")[-1]

                # Update config if auto-update enabled or user confirms
                if get_first or msg.ask(
                    f"\n[cyan]Do you want to auto update site[white] [red]'{site_name}'[cyan] with domain[white] [red]'{new_domain}'.",
                    choices=["y", "n"],
                    default="y"
                ).lower() == "y":
                    config_manager.config['SITE'][site_name]['domain'] = new_domain
                    config_manager.write_config()
                    return new_domain, f"{base_url}.{new_domain}"

    # Return original domain if no valid matches found
    console.print("[bold red]No valid URL found matching the base URL.[/bold red]")
    return domain, f"{base_url}.{domain}"