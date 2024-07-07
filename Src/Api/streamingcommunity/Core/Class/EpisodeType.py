# 03.03.24

from typing import Dict, Any, List


class Episode:
    def __init__(self, data: Dict[str, Any]):
        self.id: int = data.get('id', '')
        self.number: int = data.get('number', '')
        self.name: str = data.get('name', '')
        self.plot: str = data.get('plot', '')
        self.duration: int = data.get('duration', '')

    def __str__(self):
        return f"Episode(id={self.id}, number={self.number}, name='{self.name}', plot='{self.plot}', duration={self.duration} sec)"


class EpisodeManager:
    def __init__(self):
        self.episodes: List[Episode] = []

    def add_episode(self, episode_data: Dict[str, Any]):
        """
        Add a new episode to the manager.

        Parameters:
            - episode_data (Dict[str, Any]): A dictionary containing data for the new episode.
        """
        episode = Episode(episode_data)
        self.episodes.append(episode)

    def get(self, index: int) -> Episode:
        """
        Get an episode by its index.

        Parameters:
            - index (int): Index of the episode to retrieve.

        Returns:
            - Episode: The episode object.
        """
        return self.episodes[index]
    
    def get_length(self) -> int:
        """
        Get the number of episodes in the manager.

        Returns:
            - int: Number of episodes.
        """
        return len(self.episodes)
    
    def clear(self) -> None:
        """
        This method clears the episodes list.

        Parameters:
            - self: The object instance.
        """
        self.episodes.clear()

    def __str__(self):
        return f"EpisodeManager(num_episodes={len(self.episodes)})"
