# 03.03.24

from typing import Dict, Any, List


class Episode:
    def __init__(self, data: Dict[str, Any]):
        self.title: int = data.get('title', '')
        self.url: str = data.get('link', '')

    def __str__(self):
        return f"Episode(title='{self.title}')"


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
