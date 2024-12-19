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
        query (str): The search query to execute on Google.

    Returns:
        str: The first URL result from the search, or None if no result is found.
    """
    # Perform the search on Google and limit to 1 result
    search_results = search(query, num_results=1)
    
    # Extract the first result
    first_result = next(search_results, None)
    
    if not first_result:
        console.print("[red]No results found.[/red]")
    
    return first_result

def get_final_redirect_url(initial_url, max_timeout):
    """
    Follow redirects from the initial URL and return the final URL after all redirects.

    Args:
        initial_url (str): The URL to start with and follow redirects.

    Returns:
        str: The final URL after all redirects are followed.
    """

    # Create a client with redirects enabled
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
            response = client.get(initial_url)

            if response.status_code == 403:
                console.print("[bold red]The owner of this website has banned your IP[/bold red]")
                raise

            response.raise_for_status()
            
            # Capture the final URL after all redirects
            final_url = response.url
        
        return final_url
    
    except Exception as e:
        console.print(f"\n[cyan]Test url[white]: [red]{initial_url}, [cyan]error[white]: [red]{e}")
        return None

def search_domain(site_name: str, base_url: str):
    """
    Search for a valid domain for the given site name and base URL.

    Parameters:
        - site_name (str): The name of the site to search the domain for.
        - base_url (str): The base URL to construct complete URLs.

    Returns:
        tuple: The found domain and the complete URL.
    """

    # Extract config domain
    max_timeout = config_manager.get_int("REQUESTS", "timeout")
    domain = str(config_manager.get_dict("SITE", site_name)['domain'])

    try:
        # Test the current domain
        with httpx.Client(
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent': get_headers()
            },
            follow_redirects=True,
            timeout=max_timeout

        ) as client:
            response_follow = client.get(f"{base_url}.{domain}")
            response_follow.raise_for_status()

    except Exception as e:
        query = base_url.split("/")[-1]
        
        # Perform a Google search with multiple results
        search_results = list(search(query, num_results=5))
        #console.print(f"[green]Google search results[white]: {search_results}")

        # Iterate through search results
        for first_url in search_results:
            console.print(f"[green]Checking url[white]: [red]{first_url}")
            
            # Check if the base URL matches the Google search result
            parsed_first_url = urlparse(first_url)

            # Compare base url from google search with base url from config.json
            if parsed_first_url.netloc.split(".")[0] == base_url:
                console.print(f"[red]URL does not match base URL. Skipping.[/red]")
                continue

            try:
                final_url = get_final_redirect_url(first_url, max_timeout)

                if final_url is not None:
                    
                    def extract_domain(url):
                        parsed_url = urlparse(url)
                        domain = parsed_url.netloc
                        return domain.split(".")[-1]

                    new_domain_extract = extract_domain(str(final_url))

                    if msg.ask(f"[cyan]\nDo you want to auto site[white]: [red]{site_name}[cyan] with domain[white]: [red]{new_domain_extract}", choices=["y", "n"], default="y").lower() == "y":
                        
                        # Update domain in config.json
                        config_manager.config['SITE'][site_name]['domain'] = new_domain_extract
                        config_manager.write_config()

                        # Return config domain
                        return new_domain_extract, f"{base_url}.{new_domain_extract}"
            
            except Exception as redirect_error:
                console.print(f"[red]Error following redirect for {first_url}: {redirect_error}")
                continue

        # If no matching URL is found
        console.print("[bold red]No valid URL found matching the base URL.[/bold red]")
        raise Exception("No matching domain found")

    # Ensure the URL is in string format before parsing
    parsed_url = urlparse(str(response_follow.url))
    parse_domain = parsed_url.netloc
    tld = parse_domain.split('.')[-1]

    if tld is not None:
        # Update domain in config.json
        config_manager.config['SITE'][site_name]['domain'] = tld
        config_manager.write_config()

    # Return config domain
    return tld, f"{base_url}.{tld}"