# 03.03.24

from typing import Dict, Any, List

class Episode:
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize an Episode object.

        Args:
            data (Dict[str, Any]): A dictionary containing data for the episode.
        """
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


class EpisodeManager:
    def __init__(self):
        """
        Initialize an EpisodeManager object.
        """
        self.episodes: List[Episode] = []

    def add_episode(self, episode_data: Dict[str, Any]):
        """
        Add a new episode to the manager.

        Args:
            episode_data (Dict[str, Any]): A dictionary containing data for the new episode.
        """
        episode = Episode(episode_data)
        self.episodes.append(episode)

    def get_episode_by_index(self, index: int) -> Episode:
        """
        Get an episode by its index.

        Args:
            index (int): Index of the episode to retrieve.

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
            self: The object instance.
        """
        self.episodes.clear()
