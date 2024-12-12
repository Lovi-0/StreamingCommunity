# 23.11.24

import re
import logging
from typing import Dict, Any, List, Union


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

        Parameters:
            - self: The object instance.
        """
        self.episodes.clear()

    def __str__(self):
        return f"EpisodeManager(num_episodes={len(self.episodes)})"


class Season:
    def __init__(self, season_data: Dict[str, Union[int, str, None]]):
        self.id: int = season_data.get('id')
        self.number: int = season_data.get('number')
        self.name: str = season_data.get('name')
        self.plot: str = season_data.get('plot')
        self.episodes_count: int = season_data.get('episodes_count')

    def __str__(self):
        return f"Season(id={self.id}, number={self.number}, name='{self.name}', plot='{self.plot}', episodes_count={self.episodes_count})"

class SeasonManager:
    def __init__(self):
        self.seasons: List[Season] = []

    def add_season(self, season_data: Dict[str, Union[int, str, None]]):
        """
        Add a new season to the manager.

        Parameters:
            season_data (Dict[str, Union[int, str, None]]): A dictionary containing data for the new season.
        """
        season = Season(season_data)
        self.seasons.append(season)

    def get(self, index: int) -> Season:
        """
        Get a season item from the list by index.

        Parameters:
            index (int): The index of the seasons item to retrieve.

        Returns:
            Season: The media item at the specified index.
        """
        return self.media_list[index]

    def get_length(self) -> int:
        """
        Get the number of seasons in the manager.

        Returns:
            int: Number of seasons.
        """
        return len(self.seasons)
    
    def clear(self) -> None:
        """
        This method clears the seasons list.

        Parameters:
            self: The object instance.
        """
        self.seasons.clear()

    def __str__(self):
        return f"SeasonManager(num_seasons={len(self.seasons)})"


class Stream:
    def __init__(self, name: str, url: str, active: bool):
        self.name = name
        self.url = url
        self.active = active

    def __repr__(self):
        return f"Stream(name={self.name!r}, url={self.url!r}, active={self.active!r})"

class StreamsCollection:
    def __init__(self, streams: list):
        self.streams = [Stream(**stream) for stream in streams]

    def __repr__(self):
        return f"StreamsCollection(streams={self.streams})"

    def add_stream(self, name: str, url: str, active: bool):
        self.streams.append(Stream(name, url, active))

    def get_streams(self):
        return self.streams

    
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
        params = data.get('params', {})
        self.token: str = params.get('token', '')
        self.expires: str = str(params.get('expires', ''))
        self.url = data.get('url')

    def __str__(self):
        return (f"WindowParameter(token='{self.token}', expires='{self.expires}', url='{self.url}', data={self.data})")
