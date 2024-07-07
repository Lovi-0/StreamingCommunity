# 03.03.24

from typing import List, Dict, Union


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
