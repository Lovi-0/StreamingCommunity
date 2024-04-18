# 03.03.24

from typing import List

class Image:
    def __init__(self, data: dict):
        """
        Initialize an Image object.

        Args:
            data (dict): Data for initializing the Image.
        """
        self.imageable_id: int = data.get('imageable_id')
        self.imageable_type: str = data.get('imageable_type')
        self.filename: str = data.get('filename')
        self.type: str = data.get('type')
        self.original_url_field: str = data.get('original_url_field')


class MediaItem:
    def __init__(self, data: dict):
        """
        Initialize a MediaItem object.

        Args:
            data (dict): Data for initializing the MediaItem.
        """
        self.id: int = data.get('id')
        self.slug: str = data.get('slug')
        self.name: str = data.get('name')
        self.type: str = data.get('type')
        self.score: str = data.get('score')
        self.sub_ita: int = data.get('sub_ita')
        self.last_air_date: str = data.get('last_air_date')
        self.seasons_count: int = data.get('seasons_count')
        
        # Create Image objects for each image in the data
        self.images: List[Image] = [Image(image_data) for image_data in data.get('images', [])]
        self.comment: str = ""  # Initialize comment as an empty string

    @property
    def to_dict(self) -> dict:
        """
        Convert the MediaItem to a dictionary.

        Returns:
            dict: The MediaItem as a dictionary.
        """
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "type": self.type.upper(),
            "score": self.score,
            "sub_ita": self.sub_ita,
            "last_air_date": self.last_air_date,
            "seasons_count": self.seasons_count,
            "images": [image.__dict__ for image in self.images],
            "comment": self.comment
        }

    @property
    def get_site_id(self) -> str:
        """
        Get the site ID of the media item.

        Returns:
            int: The site ID of the media item.
        """
        return f"{self.id}-{self.slug}"


class MediaManager:
    def __init__(self):
        """
        Initialize a MediaManager object.
        """
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

