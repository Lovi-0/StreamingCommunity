# 18.06.24

import sys
from urllib.parse import urlparse


# External libraries
import httpx
from googlesearch import search


# Internal utilities
from StreamingCommunity.Src.Util.headers import get_headers
from StreamingCommunity.Src.Util.console import console, msg
from StreamingCommunity.Src.Util._jsonConfig import config_manager


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
        with httpx.Client(follow_redirects=True, timeout=max_timeout, headers={'user-agent': get_headers()}) as client:
            response = client.get(initial_url)
            response.raise_for_status()
            
            # Capture the final URL after all redirects
            final_url = response.url
        
        return final_url
    
    except Exception as e:
        console.print(f"[cyan]Test url[white]: [red]{initial_url}, [cyan]error[white]: [red]{e}")
        return None

def search_domain(site_name: str, base_url: str):
    """
    Search for a valid domain for the given site name and base URL.

    Parameters:
        - site_name (str): The name of the site to search the domain for.
        - base_url (str): The base URL to construct complete URLs.
        - follow_redirects (bool): To follow redirect url or not.

    Returns:
        tuple: The found domain and the complete URL.
    """

    # Extract config domain
    max_timeout = config_manager.get_int("REQUESTS", "timeout")
    domain = str(config_manager.get_dict("SITE", site_name)['domain'])

    try:

        # Test the current domain
        response_follow = httpx.get(f"{base_url}.{domain}", headers={'user-agent': get_headers()}, timeout=max_timeout, follow_redirects=True)
        response_follow.raise_for_status()

    except Exception as e:

        query = base_url.split("/")[-1]
        first_url = google_search(query)
        console.print(f"[green]First url from google seach[white]: [red]{first_url}")

        if first_url:
            final_url = get_final_redirect_url(first_url, max_timeout)

            if final_url != None:
                console.print(f"\n[bold yellow]Suggestion:[/bold yellow] [white](Experimental)\n"
                            f"[cyan]New final URL[white]: [green]{final_url}")
                
                def extract_domain(url):
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc
                    return domain.split(".")[-1]

                new_domain_extract = extract_domain(str(final_url))

                if msg.ask(f"[red]Do you want to auto update config.json - '[green]{site_name}[red]' with domain: [green]{new_domain_extract}", choices=["y", "n"], default="y").lower() == "y":
                    
                    # Update domain in config.json
                    config_manager.config['SITE'][site_name]['domain'] = new_domain_extract
                    config_manager.write_config()

                    # Return config domain
                    #console.print(f"[cyan]Return domain: [red]{new_domain_extract} \n")
                    return new_domain_extract, f"{base_url}.{new_domain_extract}"
            
            else:
                console.print("[bold red]\nManually change the domain in the JSON file.[/bold red]")
                raise

        else:
            console.print("[bold red]No valid URL to follow redirects.[/bold red]")

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
