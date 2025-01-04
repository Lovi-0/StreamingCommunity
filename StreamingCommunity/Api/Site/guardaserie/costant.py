# 09.06.24

import os


# Internal utilities
from StreamingCommunity.Util._jsonConfig import config_manager


SITE_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
DOMAIN_NOW = config_manager.get_dict('SITE', SITE_NAME)['domain']

SERIES_FOLDER = os.path.join(ROOT_PATH, config_manager.get('DEFAULT', 'serie_folder_name'))
MOVIE_FOLDER = os.path.join(ROOT_PATH, config_manager.get('DEFAULT', 'movie_folder_name'))

if config_manager.get_bool("DEFAULT", "add_siteName"):
    SERIES_FOLDER = os.path.join(ROOT_PATH, SITE_NAME, config_manager.get('DEFAULT', 'serie_folder_name'))
    MOVIE_FOLDER = os.path.join(ROOT_PATH, SITE_NAME, config_manager.get('DEFAULT', 'movie_folder_name'))   
