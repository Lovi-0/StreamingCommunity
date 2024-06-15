# 09.06.24

# Internal utilities
from Src.Util._jsonConfig import config_manager


SITE_NAME = "ddlstreamitaly"
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
DOMAIN_NOW = config_manager.get('SITE', SITE_NAME)

MOVIE_FOLDER = "Movie"
SERIES_FOLDER = "Serie"
