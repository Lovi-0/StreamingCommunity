# 03.03.24

from typing import List, Dict, Union


class Season:
    def __init__(self, season_data: Dict[str, Union[int, str, None]]):
        self.id: int = season_data.get('id')
        self.number: int = season_data.get('number')
        self.name: str = season_data.get('name')
        self.plot: str = season_data.get('plot')
        self.release_date: str = season_data.get('release_date')
        self.title_id: int = season_data.get('title_id')
        self.created_at: str = season_data.get('created_at')
        self.updated_at: str = season_data.get('updated_at')
        self.episodes_count: int = season_data.get('episodes_count')

    def __str__(self):
        return f"Season(id={self.id}, number={self.number}, name='{self.name}', plot='{self.plot}', release_date='{self.release_date}', title_id={self.title_id}, created_at='{self.created_at}', updated_at='{self.updated_at}', episodes_count={self.episodes_count})"


class SeasonManager:
    def __init__(self):
        self.seasons: List[Season] = []

    def add_season(self, season_data: Dict[str, Union[int, str, None]]):
        """
        Add a new season to the manager.

        Args:
            season_data (Dict[str, Union[int, str, None]]): A dictionary containing data for the new season.
        """
        season = Season(season_data)
        self.seasons.append(season)

    def get_season_by_index(self, index: int) -> Season:
        """
        Get a season by its index.

        Args:
            index (int): Index of the season to retrieve.

        Returns:
            Season: The season object.
        """
        return self.seasons[index]
    
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

        Args:
            self: The object instance.
        """
        self.seasons.clear()

    def __str__(self):
        return f"SeasonManager(num_seasons={len(self.seasons)})"
