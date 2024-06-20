# 03.03.24

from typing import List


# Variable
from ...costant import SITE_NAME, DOMAIN_NOW



class MediaItem:
    def __init__(self, data: dict):
        self.id: int = data.get('id')
        self.slug: str = data.get('slug')
        self.name: str = data.get('name')
        self.type: str = data.get('type')
        self.score: str = data.get('score')
        self.sub_ita: int = data.get('sub_ita')
        self.last_air_date: str = data.get('last_air_date')
        self.seasons_count: int = data.get('seasons_count')

    def __str__(self):
        return f"MediaItem(id={self.id}, slug='{self.slug}', name='{self.name}', type='{self.type}', score='{self.score}', sub_ita={self.sub_ita}, last_air_date='{self.last_air_date}', seasons_count={self.seasons_count})"


class MediaManager:
    def __init__(self):
        self.media_list: List[MediaItem] = []

    def add_media(self, data: dict) -> None:
        """
        Add media to the list.

        Args:
            data (dict): Media data to add.
        """
        self.media_list.append(MediaItem(data))

    def get(self, index: int) -> MediaItem:
        """
        Get a media item from the list by index.

        Args:
            index (int): The index of the media item to retrieve.

        Returns:
            MediaItem: The media item at the specified index.
        """
        return self.media_list[index]
    
    def get_length(self) -> int:
        """
        Get the number of media find with research

        Returns:
            int: Number of episodes.
        """
        return len(self.media_list)

    def clear(self) -> None:
        """
        This method clears the medias list.

        Args:
            self: The object instance.
        """
        self.media_list.clear()

    def __str__(self):
        return f"MediaManager(num_media={len(self.media_list)})"

