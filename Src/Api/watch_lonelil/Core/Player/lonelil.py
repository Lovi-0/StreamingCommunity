
# 29.06.24
import sys 
import json
import urllib.parse


# Logic class
from ..Class.SearchType import MediaItem 
from Src.Lib.Driver import WebAutomation

# Variable
from ...costant import SITE_NAME, DOMAIN_NOW 
full_site_name=f"{SITE_NAME}.{DOMAIN_NOW}"


class ApiManager:
    """
    A class to manage API interactions for media items.
    """
    def __init__(self, media: MediaItem, main_driver: WebAutomation) -> None: 
        """
        Initializes the ApiManager with a media item and a web automation driver.

        Args:
            - media (MediaItem): The media item to be processed.
            - main_driver (WebAutomation): The driver to perform web automation tasks.
        """
        self.media = media
        self.id = self.media.url.split("/")[-1]
        self.main_driver = main_driver

    def get_playlist(self) -> str:
        """
        Retrieves the URL of the best quality stream available for the media item.
        
        Returns:
            - str: The URL of the best quality stream.
        """

        # Prepare the JSON payload
        json_payload = {
            "0": {
                "json": {
                    "type": self.media.type,
                    "id": self.id,
                    "provider": "showbox-internal"
                }
            }
        }

        # Convert the payload to a JSON string and properly escape it
        json_string = json.dumps (json_payload)
        encoded_json_string = urllib.parse.quote(json_string)

        # Format the URL with the encoded JSON string
        api_url = f"https://{full_site_name}/api/trpc/provider.run?batch=1&input={encoded_json_string}"

        # Load the API URL in the web driver
        self.main_driver.get_page(str(api_url))

        # Retrieve and parse the page content 
        soup = self.main_driver.retrieve_soup() 
        content = soup.find("pre").text
        data = json.loads(content)[0]['result']['data']['json']['stream'][0]['qualities']

        # Return the URL based on the available quality
        if len(data.keys()) == 1:
            return data.get('360')['url']
        
        if len(data.keys()) == 2:
            return data.get("720")['url']
        
        if len(data.keys()) == 3:
            return data.get('1080')['url']
        
        if len(data.keys()) == 4:
            return data.get('4k')['url']
