# 26.03.24

# Class import
from Src.Util.config import config_manager

# Import
import logging
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self):
        """
        Initialize the Logger class.
        """

        # Fetching configuration values
        self.DEBUG_MODE = config_manager.get_bool("DEFAULT", "debug")
        self.log_to_file = config_manager.get_bool("DEFAULT", "log_to_file")
        self.log_file = config_manager.get("DEFAULT", "log_file") if self.log_to_file else None

        # Setting logging level based on DEBUG_MODE
        if self.DEBUG_MODE:
            self.level = logging.DEBUG

            # Configure file logging if debug mode and logging to file are both enabled
            if self.log_to_file:
                self.configure_file_logging()
        else:

            # If DEBUG_MODE is False, set logging level to ERROR
            self.level = logging.ERROR

        # Configure console logging
        self.configure_logging()

    def configure_logging(self):
        """
        Configure console logging.
        """
        logging.basicConfig(level=self.level, format='[%(filename)s:%(lineno)s - %(funcName)20s() ] %(asctime)s - %(levelname)s - %(message)s')

    def configure_file_logging(self):
        """
        Configure file logging if enabled.
        """

        file_handler = RotatingFileHandler(self.log_file, maxBytes=10*1024*1024, backupCount=5)

        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(filename)s:%(lineno)s - %(funcName)20s() ] %(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logging.getLogger('').addHandler(file_handler)
