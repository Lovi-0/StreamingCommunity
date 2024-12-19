# 12.14.24

import logging
import asyncio
from typing import List, Dict, Optional


# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from StreamingCommunity.Util._jsonConfig import config_manager
from StreamingCommunity.Util.headers import get_headers
from StreamingCommunity.Util.console import console


# Variable
max_timeout = config_manager.get_int("REQUESTS", "timeout")


class IlCorsaroNeroScraper:
    def __init__(self, base_url: str, max_page: int = 1):
        self.base_url = base_url
        self.max_page = max_page
        self.headers = {
            'User-Agent': get_headers(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    async def fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content of a given URL.
        """
        try:
            console.print(f"[cyan]Fetching url[white]: [red]{url}")
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=max_timeout) as client:
                response = await client.get(url)
                
                # If the request was successful, return the HTML content
                response.raise_for_status()
                return response.text
            
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    def parse_torrents(self, html: str) -> List[Dict[str, str]]:
        """
        Parse the HTML content and extract torrent details.
        """
        torrents = []
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("tbody")
        
        for row in table.find_all("tr"):
            try:
                columns = row.find_all("td")

                torrents.append({
                    'type': columns[0].get_text(strip=True),
                    'name': row.find("th").find("a").get_text(strip=True),
                    'seed': columns[1].get_text(strip=True),
                    'leech': columns[2].get_text(strip=True),
                    'size': columns[3].get_text(strip=True),
                    'date': columns[4].get_text(strip=True),
                    'url': "https://ilcorsaronero.link" + row.find("th").find("a").get("href")
                })

            except Exception as e:
                logging.error(f"Error parsing row: {e}")
                continue

        return torrents
    
    async def fetch_real_url(self, url: str) -> Optional[str]:
        """
        Fetch the real torrent URL from the detailed page.
        """
        response_html = await self.fetch_url(url)
        if not response_html:
            return None
        
        soup = BeautifulSoup(response_html, "html.parser")
        links = soup.find_all("a")

        # Find and return the magnet link
        for link in links:
            if "magnet" in str(link):
                return link.get("href")
            
        return None

    async def search(self, query: str) -> List[Dict[str, str]]:
        """
        Search for torrents based on the query string.
        """
        all_torrents = []
        
        # Loop through each page
        for page in range(self.max_page):
            url = f'{self.base_url}search?q={query}&page={page}'

            html = await self.fetch_url(url)
            if not html:
                console.print(f"[bold red]No HTML content for page {page}[/bold red]")
                break

            torrents = self.parse_torrents(html)
            if not torrents:
                console.print(f"[bold red]No torrents found on page {page}[/bold red]")
                break

            # Use asyncio.gather to fetch all real URLs concurrently
            tasks = [self.fetch_real_url(result['url']) for result in torrents]
            real_urls = await asyncio.gather(*tasks)

            # Attach real URLs to the torrent data
            for i, result in enumerate(torrents):
                result['url'] = real_urls[i]

            all_torrents.extend(torrents)

        return all_torrents

async def main():
    scraper = IlCorsaroNeroScraper("https://ilcorsaronero.link/")
    results = await scraper.search("cars")
    
    if results:
        for i, torrent in enumerate(results):
            console.print(f"[bold green]{i} = {torrent}[/bold green] \n")
    else:
        console.print("[bold red]No torrents found.[/bold red]")

if __name__ == '__main__':
    asyncio.run(main())
