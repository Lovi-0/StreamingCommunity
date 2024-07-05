# 03.07.24

from typing import List


class MediaItem:
    def __init__(self, data: dict):
        self.name: str = data.get('name')
        self.url: int = data.get('url')
        self.desc: int = data.get('desc')

    def __str__(self):
        return f"MediaItem(name='{self.name}', desc='{self.desc}', url={self.url})"


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
