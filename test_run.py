# 26.11.24

import sys
from StreamingCommunity.run import main
from StreamingCommunity.TelegramHelp.request_manager import RequestManager
from StreamingCommunity.TelegramHelp.session import set_session

# Svuoto il file
request_manager = RequestManager()
request_manager.clear_file()
script_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"

set_session(script_id)
main(script_id)