# 09.06.24

# Internal utilities
from Src.Util._jsonConfig import config_manager


SITE_NAME = "guardaserie"
ROOT_PATH = config_manager.get('DEFAULT', 'root_path')
DOMAIN_NOW = config_manager.get('SITE', SITE_NAME)

SERIES_FOLDER = "Serie"
