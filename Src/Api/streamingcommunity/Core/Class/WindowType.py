# 03.03.24

import re
import logging

from typing import Dict, Any


class WindowVideo:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.id: int = data.get('id', '')
        self.name: str = data.get('name', '')
        self.filename: str = data.get('filename', '')
        self.size: str = data.get('size', '')
        self.quality: str = data.get('quality', '')
        self.duration: str = data.get('duration', '')
        self.views: int = data.get('views', '')
        self.is_viewable: bool = data.get('is_viewable', '')
        self.status: str = data.get('status', '')
        self.fps: float = data.get('fps', '')
        self.legacy: bool = data.get('legacy', '')
        self.folder_id: int = data.get('folder_id', '')
        self.created_at_diff: str = data.get('created_at_diff', '')

    def __str__(self):
        return f"WindowVideo(id={self.id}, name='{self.name}', filename='{self.filename}', size='{self.size}', quality='{self.quality}', duration='{self.duration}', views={self.views}, is_viewable={self.is_viewable}, status='{self.status}', fps={self.fps}, legacy={self.legacy}, folder_id={self.folder_id}, created_at_diff='{self.created_at_diff}')"


class WindowParameter:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.token: str = data.get('token', '')
        self.token360p: str = data.get('token360p', '')
        self.token480p: str = data.get('token480p', '')
        self.token720p: str = data.get('token720p', '')
        self.token1080p: str = data.get('token1080p', '')
        self.expires: str = data.get('expires', '')

    def __str__(self):
        return f"WindowParameter(token='{self.token}', token360p='{self.token360p}', token480p='{self.token480p}', token720p='{self.token720p}', token1080p='{self.token1080p}', expires='{self.expires}')"
    

class DynamicJSONConverter:
    """
    Class for converting an input string into dynamic JSON.
    """

    def __init__(self, input_string: str):
        """
        Initialize the converter with the input string.

        Parameters:
            input_string (str): The input string to convert.
        """
        self.input_string = input_string
        self.json_data = {}

    def _parse_key_value(self, key: str, value: str):
        """
        Parse a key-value pair.

        Parameters:
            key (str): The key.
            value (str): The value.

        Returns:
            object: The parsed value.
        """
        try:
            value = value.strip()
 
            if value.startswith('{'):
                return self._parse_json_object(value)          
            else:
                return self._parse_non_json_value(value)
            
        except Exception as e:
            logging.error(f"Error parsing key-value pair '{key}': {e}")
            raise

    def _parse_json_object(self, obj_str: str):
        """
        Parse a JSON object.

        Parameters:
            obj_str (str): The string representation of the JSON object.

        Returns:
            dict: The parsed JSON object.
        """
        try:
            # Use regular expression to find key-value pairs in the JSON object string
            obj_dict = dict(re.findall(r'"([^"]*)"\s*:\s*("[^"]*"|[^,]*)', obj_str))

            # Strip double quotes from values and return the parsed dictionary
            return {k: v.strip('"') for k, v in obj_dict.items()}
        
        except Exception as e:
            logging.error(f"Error parsing JSON object: {e}")
            raise

    def _parse_non_json_value(self, value: str):
        """
        Parse a non-JSON value.

        Parameters:
            value (str): The value to parse.

        Returns:
            object: The parsed value.
        """
        try:

            # Remove extra quotes and convert to lowercase
            value = value.replace('"', "").strip().lower()

            if value.endswith('\n}'):
                value = value.replace('\n}', '')

                # Check if the value matches 'true' or 'false' using regular expressions
                if re.match(r'\btrue\b', value, re.IGNORECASE):
                    return True
                
                elif re.match(r'\bfalse\b', value, re.IGNORECASE):
                    return False
                
            return value
        
        except Exception as e:
            logging.error(f"Error parsing non-JSON value: {e}")
            raise

    def convert_to_dynamic_json(self):
        """
        Convert the input string into dynamic JSON.

        Returns:
            str: The JSON representation of the result.
        """
        try:

            # Replace invalid characters with valid JSON syntax
            self.input_string = "{" + self.input_string.replace("'", '"').replace("=", ":").replace(";", ",").replace("}\n", "},\n") + "}"

            # Find all key-value matches in the input string using regular expression
            matches = re.findall(r'(\w+)\s*:\s*({[^}]*}|[^,]+)', self.input_string)

            for match in matches:
                key = match[0].strip()
                value = match[1].strip()

                # Parse each key-value pair and add it to the json_data dictionary
                self.json_data[key] = self._parse_key_value(key, value)

            # Convert the json_data dictionary to a formatted JSON string
            return self.json_data
        
        except Exception as e:
            logging.error(f"Error converting to dynamic JSON: {e}")
            raise
