# 03.03.24

from typing import List, Dict, Union


class Title:
    def __init__(self, title_data: Dict[str, Union[int, str, None]]):
        """
        Initialize a Title object.

        Args:
            title_data (Dict[str, Union[int, str, None]]): A dictionary containing data for the title.
        """
        self.id: int = title_data.get('id')
        self.number: int = title_data.get('number')
        self.name: str = title_data.get('name')
        self.plot: str = title_data.get('plot')
        self.release_date: str = title_data.get('release_date')
        self.title_id: int = title_data.get('title_id')
        self.created_at: str = title_data.get('created_at')
        self.updated_at: str = title_data.get('updated_at')
        self.episodes_count: int = title_data.get('episodes_count')


class TitleManager:
    def __init__(self):
        """
        Initialize a TitleManager object.

        Args:
            titles (List[Title]): A list of Title objects. Defaults to an empty list.
        """
        self.titles: List[Title] = []

    def add_title(self, title_data: Dict[str, Union[int, str, None]]):
        """
        Add a new title to the manager.

        Args:
            title_data (Dict[str, Union[int, str, None]]): A dictionary containing data for the new title.
        """
        title = Title(title_data)
        self.titles.append(title)

    def get_title_by_index(self, index: int) -> Title:
        """
        Get a title by its index.

        Args:
            index (int): Index of the title to retrieve.

        Returns:
            Title: The title object.
        """
        return self.titles[index]
    
    def get_length(self) -> int:
        """
        Get the number of titles in the manager.

        Returns:
            int: Number of titles.
        """
        return len(self.titles)
    
    def clear(self) -> None:
        """
        This method clears the titles list.

        Args:
            self: The object instance.
        """
        self.titles.clear()