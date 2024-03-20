import json, os

class ConfigManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_config(self):
        with open(self.file_path, 'r') as file:
            config_file = json.load(file)
        return config_file

    def update_config(self, key, new_value):
        config = self.load_config()
        config[key] = new_value
        with open(self.file_path, 'w') as file:
            json.dump(config, file, indent=4)

            
# Example usage:
config_path = os.path.join('config.json')
config_manager = ConfigManager(config_path)
config = config_manager.load_config()
