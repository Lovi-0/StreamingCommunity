# 03.03.24

from typing import Dict, Any, List


# Internal utilities
from Src.Util._jsonConfig import config_manager


# Config
SC_SITE_NAME = "streamingcommunity"
SC_DOMAIN_NOW = config_manager.get('SITE', SC_SITE_NAME)



class Image:
    def __init__(self, image_data: Dict[str, Any]):
        self.id: int = image_data.get('id', '')
        self.filename: str = image_data.get('filename', '')
        self.type: str = image_data.get('type', '')
        self.imageable_type: str = image_data.get('imageable_type', '')
        self.imageable_id: int = image_data.get('imageable_id', '')
        self.created_at: str = image_data.get('created_at', '')
        self.updated_at: str = image_data.get('updated_at', '')
        self.original_url_field: str = image_data.get('original_url_field', '')
        self.url: str = f"https://cdn.{SC_SITE_NAME}.{SC_DOMAIN_NOW}/images/{self.filename}"

    def __str__(self):
        return f"Image(id={self.id}, filename='{self.filename}', type='{self.type}', imageable_type='{self.imageable_type}', url='{self.url}')"


class Episode:
    def __init__(self, data: Dict[str, Any]):
        self.id: int = data.get('id', '')
        self.number: int = data.get('number', '')
        self.name: str = data.get('name', '')
        self.plot: str = data.get('plot', '')
        self.duration: int = data.get('duration', '')
        self.scws_id: int = data.get('scws_id', '')
        self.season_id: int = data.get('season_id', '')
        self.created_by: str = data.get('created_by', '')
        self.created_at: str = data.get('created_at', '')
        self.updated_at: str = data.get('updated_at', '')
        self.images: List[Image] = [Image(image_data) for image_data in data.get('images', [])]

    def __str__(self):
        return f"Episode(id={self.id}, number={self.number}, name='{self.name}', plot='{self.plot}', duration={self.duration} sec)"


class EpisodeManager:
    def __init__(self):
        self.episodes: List[Episode] = []

    def add_episode(self, episode_data: Dict[str, Any]):
        """
        Add a new episode to the manager.

        Args:
            - episode_data (Dict[str, Any]): A dictionary containing data for the new episode.
        """
        episode = Episode(episode_data)
        self.episodes.append(episode)

    def get_episode_by_index(self, index: int) -> Episode:
        """
        Get an episode by its index.

        Args:
            - index (int): Index of the episode to retrieve.

        Returns:
            Episode: The episode object.
        """
        return self.episodes[index]
    
    def get_length(self) -> int:
        """
        Get the number of episodes in the manager.

        Returns:
            int: Number of episodes.
        """
        return len(self.episodes)
    
    def clear(self) -> None:
        """
        This method clears the episodes list.

        Args:
            - self: The object instance.
        """
        self.episodes.clear()

    def __str__(self):
        return f"EpisodeManager(num_episodes={len(self.episodes)})"
