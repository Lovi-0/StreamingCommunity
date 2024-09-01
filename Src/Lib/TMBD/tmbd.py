# 24.08.24

from typing import Dict


# External libraries
import httpx
from rich.console import Console


# Internal utilities
from Src.Util.table import TVShowManager


# Variable
tv_show_manager = TVShowManager()
api_key = "a800ed6c93274fb857ea61bd9e7256c5"


class TheMovieDB:
    def __init__(self, api_key):
        """
        Initialize the class with the API key and TV show manager.
        
        Parameters:
            - api_key (str): The API key for authenticating requests to TheMovieDB.
            - tv_show_manager (TVShowManager): An instance of the TVShowManager for handling TV show items.
        """
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.console = Console()
        self.genres = self._fetch_genres()

    def _make_request(self, endpoint, params=None):
        """
        Make a request to the given API endpoint with optional parameters.
        
        Parameters:
            - endpoint (str): The API endpoint to hit.
            - params (dict): Additional parameters for the request.
        
        Returns:
            dict: JSON response as a dictionary.
        """
        if params is None:
            params = {}

        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        response = httpx.get(url, params=params)
        response.raise_for_status()
        
        return response.json()

    def _fetch_genres(self) -> Dict[int, str]:
        """
        Fetch and return the genre names from TheMovieDB.

        Returns:
            Dict[int, str]: A dictionary mapping genre IDs to genre names.
        """
        genres = self._make_request("genre/tv/list")
        return {genre['id']: genre['name'] for genre in genres.get('genres', [])}

    def _process_and_add_tv_shows(self, data, columns):
        """
        Process TV show data and add it to the TV show manager.
        
        Parameters:
            - data (list): List of dictionaries containing the data to process.
            - columns (list): A list of tuples, where each tuple contains the column name and the key to fetch the data from the dictionary.
        """
        # Define column styles with colors
        tv_show_manager = TVShowManager()
        column_info = {
            col[0]: {'color': col[2] if len(col) > 2 else 'white'}
            for col in columns
        }
        tv_show_manager.add_column(column_info)

        # Add each item to the TV show manager, including rank
        for index, item in enumerate(data):
            
            # Convert genre IDs to genre names
            genre_names = [self.genres.get(genre_id, 'Unknown') for genre_id in item.get('genre_ids', [])]
            tv_show = {
                col[0]: str(item.get(col[1], 'N/A')) if col[1] != 'genre_ids' else ', '.join(genre_names)
                for col in columns
            }

            tv_show_manager.add_tv_show(tv_show)
        
        # Display the processed TV show data
        tv_show_manager.display_data(tv_show_manager.tv_shows[tv_show_manager.slice_start:tv_show_manager.slice_end])

    def _display_with_title(self, title: str, data, columns):
        """
        Display data with a title.

        Parameters:
            - title (str): The title to display.
            - data (list): List of dictionaries containing the data to process.
            - columns (list): A list of tuples, where each tuple contains the column name and the key to fetch the data from the dictionary.
        """
        self.console.print(f"\n{title}", style="bold underline")
        self._process_and_add_tv_shows(data, columns)

    def display_trending_tv_shows(self):
        """
        Fetch and display the trending TV shows of the week.
        """
        data = self._make_request("trending/tv/week").get("results", [])
        columns = [
            ("Title", "name", 'cyan'), 
            ("First Air Date", "first_air_date", 'green'), 
            ("Popularity", "popularity", 'magenta'),
            ("Genres", "genre_ids", 'blue'),
            ("Origin Country", "origin_country", 'red'),
            ("Vote Average", "vote_average", 'yellow')
        ]
        self._display_with_title("Trending TV Shows of the Week", data, columns)

    def display_trending_films(self):
        """
        Fetch and display the trending films of the week.
        """
        data = self._make_request("trending/movie/week").get("results", [])
        columns = [
            ("Title", "title", 'cyan'), 
            ("Release Date", "release_date", 'green'), 
            ("Popularity", "popularity", 'magenta'),
            ("Genres", "genre_ids", 'blue'),
            ("Vote Average", "vote_average", 'yellow')
        ]
        self._display_with_title("Trending Films of the Week", data, columns)

# Output
tmdb = TheMovieDB(api_key)