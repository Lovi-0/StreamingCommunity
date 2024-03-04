import json
from pathlib import Path

def load_config(file_path):
    with open(file_path, 'r') as file:
        config_file = json.load(file)
    return config_file

config_path = Path(__file__).parent.parent.parent / 'config.json' # path for config.json (in root directory)
config = load_config(config_path)