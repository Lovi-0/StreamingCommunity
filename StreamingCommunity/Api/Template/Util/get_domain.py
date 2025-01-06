# 18.06.24

from urllib.parse import urlparse, unquote


# External libraries
import httpx
from googlesearch import search


# Internal utilities
from StreamingCommunity.Util.headers import get_headers
from StreamingCommunity.Util.console import console, msg
from StreamingCommunity.Util._jsonConfig import config_manager


def get_tld(url_str):
    """Extract the TLD (Top-Level Domain) from the URL without using external libraries."""
    url_str = unquote(url_str)
    
    parsed = urlparse(url_str)
    domain = parsed.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]
    
    parts = domain.split('.')
    
    if len(parts) >= 2:
        return parts[-1]
    return None

def get_base_domain(url_str):
    """Extract base domain without protocol, www and path"""
    parsed = urlparse(url_str)
    domain = parsed.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain.split('.')[0]

def validate_url(url, base_url, max_timeout):
    """
    Validate if URL is accessible and matches expected base domain
    """
    console.print(f"\n[cyan]Starting validation for URL[white]: [yellow]{url}")
    
    def check_response(response, check_num):
        if response.status_code == 403:
            console.print(f"[red]Check {check_num} failed: Access forbidden (403)")
            return False
        if response.status_code >= 400:
            console.print(f"[red]Check {check_num} failed: HTTP {response.status_code}")
            return False
        console.print(f"[green]Check {check_num} passed: HTTP {response.status_code}")
        return True

    try:
        
        # Check 1: Initial request without following redirects
        console.print("[cyan]Performing initial connection check...")
        with httpx.Client(
            headers={'User-Agent': get_headers()},
            follow_redirects=False,
            timeout=max_timeout
        ) as client:
            response = client.get(url)
            if not check_response(response, 1):
                return False, None

        # Check 2: Follow redirects and verify final domain
        console.print("[cyan]Checking redirect destination...")
        with httpx.Client(
            headers={'User-Agent': get_headers()},
            follow_redirects=True,
            timeout=max_timeout
        ) as client:
            
            response = client.get(url)
            if not check_response(response, 2):
                return False, None
            
            # Compare base domains
            original_base = get_base_domain(url)
            final_base = get_base_domain(str(response.url))
            
            console.print(f"[cyan]Comparing domains:")
            console.print(f"Original base domain: [yellow]{original_base}.{get_tld(str(url))}")
            console.print(f"Final base domain: [yellow]{final_base}.{get_tld(str(response.url))}")
            
            if original_base != final_base:
                return False, None
            
            expected_base = get_base_domain(base_url)
            if final_base != expected_base:
                return False, None

            if get_tld(str(url)) != get_tld(str(response.url)):
                return True, get_tld(str(response.url))
                
            console.print(f"[green]All checks passed: URL is valid and matches expected domain")
            return True, None
            
    except Exception as e:
        console.print(f"[red]Error during validation: {str(e)}")
        return False, None

def search_domain(site_name: str, base_url: str, get_first: bool = False):
    """
    Search for valid domain matching site name and base URL.
    """
    max_timeout = config_manager.get_int("REQUESTS", "timeout")
    domain = str(config_manager.get_dict("SITE", site_name)['domain'])
    test_url = f"{base_url}.{domain}"

    console.print(f"\n[cyan]Testing initial URL[white]: [yellow]{test_url}")
    
    try:
        is_correct, redirect_tld = validate_url(test_url, base_url, max_timeout)

        if is_correct and redirect_tld is not None:
            config_manager.config['SITE'][site_name]['domain'] = redirect_tld
            config_manager.write_config()
            console.print(f"[green]Successfully validated initial URL")
            return redirect_tld, test_url

        if is_correct:
            parsed_url = urlparse(test_url)
            tld = parsed_url.netloc.split('.')[-1]
            config_manager.config['SITE'][site_name]['domain'] = tld
            config_manager.write_config()
            console.print(f"[green]Successfully validated initial URL")
            return tld, test_url
        
    except Exception as e:
        console.print(f"[red]Error testing initial URL: {str(e)}")

    # Google search phase
    query = base_url.split("/")[-1]
    console.print(f"\n[cyan]Performing Google search for[white]: [yellow]{query}")
    search_results = list(search(query, num_results=20, lang="it"))
    
    for idx, result_url in enumerate(search_results, 1):
        if get_base_domain(result_url) == get_base_domain(test_url):
            console.print(f"\n[cyan]Checking Google result {idx}/20[white]: [yellow]{result_url}")
            
            if validate_url(result_url, base_url, max_timeout):
                parsed_result = urlparse(result_url)
                new_domain = parsed_result.netloc.split(".")[-1]
                
                if get_first or msg.ask(
                    f"\n[cyan]Do you want to update site[white] [red]'{site_name}'[cyan] with domain[white] [red]'{new_domain}'",
                    choices=["y", "n"],
                    default="y"
                ).lower() == "y":
                    
                    config_manager.config['SITE'][site_name]['domain'] = new_domain
                    config_manager.write_config()
                    return new_domain, f"{base_url}.{new_domain}"

    console.print("[bold red]No valid URLs found matching the base URL.")
    return domain, f"{base_url}.{domain}"