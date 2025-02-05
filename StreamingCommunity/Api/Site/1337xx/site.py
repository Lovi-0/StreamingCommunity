# 02.07.24

# External libraries
import httpx
from bs4 import BeautifulSoup


# Internal utilities
from StreamingCommunity.Util.console import console
from StreamingCommunity.Util._jsonConfig import config_manager
from StreamingCommunity.Util.headers import get_headers
from StreamingCommunity.Util.table import TVShowManager


# Logic class
from StreamingCommunity.Api.Template import get_select_title
from StreamingCommunity.Api.Template.Util import search_domain
from StreamingCommunity.Api.Template.Class.SearchType import MediaManager

# Telegram bot instance
from StreamingCommunity.HelpTg.telegram_bot import get_bot_instance
TELEGRAM_BOT = config_manager.get_bool('DEFAULT', 'telegram_bot')


# Variable
from .costant import SITE_NAME, DOMAIN_NOW
media_search_manager = MediaManager()
table_show_manager = TVShowManager()
max_timeout = config_manager.get_int("REQUESTS", "timeout")
disable_searchDomain = config_manager.get_bool("DEFAULT", "disable_searchDomain")


def title_search(word_to_search: str) -> int:
    """
    Search for titles based on a search query.

    Parameters:
        - title_search (str): The title to search for.

    Returns:
        - int: The number of titles found.
    """

    if TELEGRAM_BOT:
      bot = get_bot_instance()

    media_search_manager.clear()
    table_show_manager.clear()

    # Find new domain if prev dont work
    domain_to_use = DOMAIN_NOW

    if not disable_searchDomain:
        domain_to_use, base_url = search_domain(SITE_NAME, f"https://{SITE_NAME}.{DOMAIN_NOW}")

    # Construct the full site URL and load the search page
    try:
        response = httpx.get(
            url=f"https://{SITE_NAME}.{domain_to_use}/search/{word_to_search}/1/", 
            headers={'user-agent': get_headers()}, 
            follow_redirects=True,
            timeout=max_timeout
        )
        response.raise_for_status()

    except Exception as e:
        console.print(f"Site: {SITE_NAME}, request search error: {e}")

    # Create soup and find table
    soup = BeautifulSoup(response.text, "html.parser")

    if TELEGRAM_BOT:
      # Inizializza la lista delle scelte
      choices = []

    for tr in soup.find_all('tr'):
        try:

            title_info = {
                'name': tr.find_all("a")[1].get_text(strip=True),
                'url': tr.find_all("a")[1].get("href"),
                'seader': tr.find_all("td")[-5].get_text(strip=True),
                'leacher': tr.find_all("td")[-4].get_text(strip=True),
                'date': tr.find_all("td")[-3].get_text(strip=True).replace("'", ""),
                'size': tr.find_all("td")[-2].get_text(strip=True)
            }

            if TELEGRAM_BOT:
              # Crea una stringa formattata per ogni scelta con numero
              choice_text = f"{len(choices)} - {title_info.get('name')} ({title_info.get('type')}) - {title_info.get('date')}"
              choices.append(choice_text)

              media_search_manager.add_media(title_info)

        except Exception as e:
            print(f"Error parsing a film entry: {e}")

    if TELEGRAM_BOT:
      # Se ci sono scelte, inviale a Telegram
      if choices:
          # Invio a telegram la lista
          bot.send_message(f"Lista dei risultati:", choices)

    # Return the number of titles found
    return media_search_manager.get_length()


def run_get_select_title():
    """
    Display a selection of titles and prompt the user to choose one.
    """
    return get_select_title(table_show_manager, media_search_manager)
