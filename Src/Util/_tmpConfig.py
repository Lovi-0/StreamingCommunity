# 11.04.24


import os
import tempfile
import configparser
import logging
import json
from typing import Union, List


# Costant
repo_name = "StreamingCommunity_api"
config_file_name = f"{repo_name}_config.ini"


class ConfigError(Exception):
    """
    Exception raised for errors related to configuration management.
    """
    def __init__(self, message: str):
        """
        Initialize ConfigError with the given error message.
        
        Args:
            message (str): The error message.
        """
        self.message = message
        super().__init__(self.message)
        logging.error(self.message)


class ConfigManager:
    """
    Class to manage configuration settings using a config file.
    """
    def __init__(self, config_file_name: str = config_file_name, defaults: dict = None):
        """
        Initialize ConfigManager.
        
        Args:
            config_file_name (str, optional): The name of the configuration file. Default is 'config.ini'.
            defaults (dict, optional): A dictionary containing default values for variables. Default is None.
        """
        self.config_file_path = os.path.join(tempfile.gettempdir(), config_file_name)
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)

        # Create config file if it doesn't exist
        if not os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'w') as config_file:
                if defaults:
                    for section, options in defaults.items():
                        if not self.config.has_section(section):
                            self.config.add_section(section)
                        for key, value in options.items():
                            self.config.set(section, key, str(value))
                    self.config.write(config_file)

        # Read existing config
        self.config.read(self.config_file_path)

    def _check_section_and_key(self, section: str, key: str) -> None:
        """
        Check if the given section and key exist in the configuration file.
        
        Args:
            section (str): The section in the config file.
            key (str): The key of the variable.
        
        Raises:
            ConfigError: If the section or key does not exist.
        """
        if not self.config.has_section(section):
            raise ConfigError(f"Section '{section}' does not exist in the configuration file.")
        if not self.config.has_option(section, key):
            raise ConfigError(f"Key '{key}' does not exist in section '{section}'.")

    def get_int(self, section: str, key: str, default: Union[int, None] = None) -> Union[int, None]:
        """
        Get the value of a variable from the config file as an integer.
        
        Args:
            section (str): The section in the config file.
            key (str): The key of the variable.
            default (int, optional): Default value if the variable doesn't exist. Default is None.
        
        Returns:
            int or None: Value of the variable as an integer or default value.
        """
        try:
            self._check_section_and_key(section, key)
            return int(self.config.get(section, key))
        except (ConfigError, ValueError):
            return default

    def get_string(self, section: str, key: str, default: Union[str, None] = None) -> Union[str, None]:
        """
        Get the value of a variable from the config file as a string.
        
        Args:
            section (str): The section in the config file.
            key (str): The key of the variable.
            default (str, optional): Default value if the variable doesn't exist. Default is None.
        
        Returns:
            str or None: Value of the variable as a string or default value.
        """
        try:
            self._check_section_and_key(section, key)
            return self.config.get(section, key)
        except ConfigError:
            return default

    def get_bool(self, section: str, key: str, default: Union[bool, None] = None) -> Union[bool, None]:
        """
        Get the value of a variable from the config file as a boolean.
        
        Args:
            section (str): The section in the config file.
            key (str): The key of the variable.
            default (bool, optional): Default value if the variable doesn't exist. Default is None.
        
        Returns:
            bool or None: Value of the variable as a boolean or default value.
        """
        try:
            self._check_section_and_key(section, key)
            return self.config.getboolean(section, key)
        except ConfigError:
            return default

    def get_list(self, section: str, key: str, default: Union[List, None] = None) -> Union[List, None]:
        """
        Get the value of a variable from the config file as a list.
        
        Args:
            section (str): The section in the config file.
            key (str): The key of the variable.
            default (List, optional): Default value if the variable doesn't exist. Default is None.
        
        Returns:
            List or None: Value of the variable as a list or default value.
        """
        try:
            self._check_section_and_key(section, key)
            value = self.config.get(section, key)
            return json.loads(value)
        except (ConfigError, json.JSONDecodeError):
            return default

    def add_variable(self, section: str, key: str, value: Union[int, str, bool, List]) -> None:
        """
        Add or update a variable in the config file.
        
        Args:
            section (str): The section in the config file.
            key (str): The key of the variable.
            value (int, str, bool, List): The value of the variable.
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        with open(self.config_file_path, 'w') as config_file:
            self.config.write(config_file)
        self.logger.info(f"Added or updated variable '{key}' in section '{section}'")

    def reload_config(self) -> None:
        """
        Reload the configuration from the file.
        """
        self.config.clear()
        self.config.read(self.config_file_path)
        self.logger.info("Configuration file reloaded")


# Output
defaults = {
    'Requirements': {
        'ffmpeg': False
    },
    'Backup' : {
        'path': False
    }
}

temp_config_manager = ConfigManager(defaults=defaults)

