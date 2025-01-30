# 18.06.24

import ssl
import time
from urllib.parse import urlparse, unquote


# External libraries
import httpx
from googlesearch import search


# Internal utilities
from StreamingCommunity.Util.headers import get_headers
from StreamingCommunity.Util.console import console, msg
from StreamingCommunity.Util._jsonConfig import config_manager

base_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
    'dnt': '1',
    'priority': 'u=0, i',
    'referer': '',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': ''
}


def get_tld(url_str):
    """Extract the TLD (Top-Level Domain) from the URL."""
    try:
        url_str = unquote(url_str)
        parsed = urlparse(url_str)
        domain = parsed.netloc.lower()

        if domain.startswith('www.'):
            domain = domain[4:]
        parts = domain.split('.')

        return parts[-1] if len(parts) >= 2 else None
    
    except Exception:
        return None

def get_base_domain(url_str):
    """Extract base domain without protocol, www and path."""
    try:
        parsed = urlparse(url_str)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]

        # Check if domain has multiple parts separated by dots
        parts = domain.split('.')
        if len(parts) > 2:  # Handle subdomains
            return '.'.join(parts[:-1])  # Return everything except TLD
        
        return parts[0]  # Return base domain
    
    except Exception:
        return None
    
def get_base_url(url_str):
    """Extract base URL including protocol and domain, removing path and query parameters."""
    try:
        parsed = urlparse(url_str)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    except Exception:
        return None

def validate_url(url, base_url, max_timeout, max_retries=2, sleep=1):
    """Validate if URL is accessible and matches expected base domain."""
    console.print(f"\n[cyan]Starting validation for URL[white]: [yellow]{url}")
    
    # Verify URL structure matches base_url structure
    base_domain = get_base_domain(base_url)
    url_domain = get_base_domain(url)

    base_headers['referer'] = url
    base_headers['user-agent'] = get_headers()
    
    if base_domain != url_domain:
        console.print(f"[red]Domain structure mismatch: {url_domain} != {base_domain}")
        return False, None
    
    # Count dots to ensure we don't have extra subdomains
    base_dots = base_url.count('.')
    url_dots = url.count('.')
    if url_dots > base_dots + 1:  # Allow for one extra dot for TLD change
        console.print(f"[red]Too many subdomains in URL")
        return False, None

    client = httpx.Client(
        verify=False,
        headers=base_headers,
        timeout=max_timeout
    )

    for retry in range(max_retries):
        try:
            time.sleep(sleep)
            
            # Initial check without redirects
            response = client.get(url, follow_redirects=False)
            if response.status_code == 403:
                console.print(f"[red]Check failed (403) - Attempt {retry + 1}/{max_retries}")
                continue
                
            if response.status_code >= 400:
                console.print(f"[red]Check failed: HTTP {response.status_code}")
                return False, None
                
            # Follow redirects and verify final domain
            final_response = client.get(url, follow_redirects=True)
            final_domain = get_base_domain(str(final_response.url))
            console.print(f"[cyan]Redirect url: [red]{final_response.url}")
            
            if final_domain != base_domain:
                console.print(f"[red]Final domain mismatch: {final_domain} != {base_domain}")
                return False, None
                
            new_tld = get_tld(str(final_response.url))
            if new_tld != get_tld(url):
                return True, new_tld
                
            return True, None
            
        except (httpx.RequestError, ssl.SSLError) as e:
            console.print(f"[red]Connection error: {str(e)}")
            time.sleep(sleep)
            continue
            
    return False, None

def search_domain(site_name: str, base_url: str, get_first: bool = False):
    """Search for valid domain matching site name and base URL."""
    max_timeout = config_manager.get_int("REQUESTS", "timeout")
    domain = str(config_manager.get_dict("SITE", site_name)['domain'])
    
    # Test initial URL
    try:
        is_correct, redirect_tld = validate_url(base_url, base_url, max_timeout)

        if is_correct:
            tld = redirect_tld or get_tld(base_url)
            config_manager.config['SITE'][site_name]['domain'] = tld
            config_manager.write_config()
            console.print(f"[green]Successfully validated initial URL")
            return tld, base_url
        
    except Exception as e:
        console.print(f"[red]Error testing initial URL: {str(e)}")

    # Google search phase
    base_domain = get_base_domain(base_url)
    console.print(f"\n[cyan]Searching for alternate domains for[white]: [yellow]{base_domain}")
    
    try:
        search_results = list(search(base_domain, num_results=20, lang="it"))

        base_urls = set()
        for url in search_results:
            element_url = get_base_url(url)
            if element_url:
                base_urls.add(element_url)
        
        # Filter URLs based on domain matching and subdomain count
        filtered_results = [
            url for url in base_urls 
            if get_base_domain(url) == base_domain 
            and url.count('.') <= base_url.count('.') + 1
        ]

        for idx, result_url in enumerate(filtered_results, 1):
            console.print(f"\n[cyan]Checking result {idx}/{len(filtered_results)}[white]: [yellow]{result_url}")
            
            is_valid, new_tld = validate_url(result_url, base_url, max_timeout)
            if is_valid:
                final_tld = new_tld or get_tld(result_url)

                if get_first or msg.ask(
                    f"\n[cyan]Update site[white] [red]'{site_name}'[cyan] with domain[white] [red]'{final_tld}'",
                    choices=["y", "n"],
                    default="y"
                ).lower() == "y":
                    
                    config_manager.config['SITE'][site_name]['domain'] = final_tld
                    config_manager.write_config()
                    return final_tld, f"{base_url}.{final_tld}"
                    
    except Exception as e:
        console.print(f"[red]Error during search: {str(e)}")

    console.print("[bold red]No valid URLs found matching the base URL.")
    return domain, f"{base_url}.{domain}"