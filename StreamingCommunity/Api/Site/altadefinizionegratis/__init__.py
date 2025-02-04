# 26.05.24

from urllib.parse import quote_plus


# Internal utilities
from StreamingCommunity.Util.console import console, msg


# Logic class
from .site import title_search, run_get_select_title, media_search_manager
from .film import download_film

# Telegram bot instance
StreamingCommunity.HelpTg. import get_bot_instance
from StreamingCommunity.Util._jsonConfig import config_manager
TELEGRAM_BOT = config_manager.get_bool('DEFAULT', 'telegram_bot')

# Variable
indice = 2
_useFor = "film"
_deprecate = False
_priority = 2
_engineDownload = "hls"
from .costant import SITE_NAME


def search(string_to_search: str = None, get_onylDatabase: bool = False):
    """
    Main function of the application for film and series.
    """

    if TELEGRAM_BOT:
      bot = get_bot_instance()

      if string_to_search is None:
          # Chiedi la scelta all'utente con il bot Telegram
          string_to_search = bot.ask(
              "key_search",
              f"Inserisci la parola da cercare\noppure 🔙 back per tornare alla scelta: ",
              None
          )

          if string_to_search == 'back':
              # Riavvia lo script
              # Chiude il processo attuale e avvia una nuova istanza dello script
              subprocess.Popen([sys.executable] + sys.argv)
              sys.exit()
    else:          
      if string_to_search is None:
          string_to_search = msg.ask(f"\n[purple]Insert word to search in [green]{SITE_NAME}").strip()

    # Search on database
    len_database = title_search(quote_plus(string_to_search))

    # Return list of elements
    if get_onylDatabase:
        return media_search_manager

    if len_database > 0:

        # Select title from list
        select_title = run_get_select_title()

        # Download only film
        download_film(select_title)

    else:
        
        if TELEGRAM_BOT:
          bot.send_message(f"Nessun risultato trovato riprova", None)
          
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")

        # Retry
        search()