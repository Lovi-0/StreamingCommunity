# 17.09.2023 -> 3.12.23

# Import
from rich.console import Console
from rich.prompt import Prompt
import logging

# Variable
msg = Prompt()
console = Console()
SAVE_DEBUG = False

class ConfigurazioneLogger:
    def __init__(self, nome_file_log='debug.log'):
        self.nome_file_log = nome_file_log
        self.configura_logger()

    def configura_logger(self):
        if SAVE_DEBUG:
            logging.basicConfig(filename=self.nome_file_log, filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

config_logger = ConfigurazioneLogger()