# 09.06.24

import os


# Internal utilities
from StreamingCommunity.Src.Util._jsonConfig import config_manager


SITE_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
DOMAIN_NOW = config_manager.get_dict('SITE', SITE_NAME)['domain']

SERIES_FOLDER = "Serie"
MOVIE_FOLDER = "Film"
