# 24.08.24

import sys
from typing import Dict


# External libraries
import httpx
from rich.console import Console


# Internal utilities
from .obj_tmbd import Json_film
from StreamingCommunity.Src.Util.table import TVShowManager


# Variable
table_show_manager = TVShowManager()
api_key = "a800ed6c93274fb857ea61bd9e7256c5"



def get_select_title(table_show_manager, generic_obj):
    """
    Display a selection of titles and prompt the user to choose one.

    Returns:
        dict: The selected media item.
    """

    # Set up table for displaying titles
    table_show_manager.set_slice_end(10)

    # Check if the generic_obj list is empty
    if not generic_obj:
        Console.print("\n[red]No media items available.")
        return None
    
    # Example of available colors for columns
    available_colors = ['red', 'magenta', 'yellow', 'cyan', 'green', 'blue', 'white']
    
    # Retrieve the keys of the first item as column headers
    first_item = generic_obj[0]
    column_info = {"Index": {'color': available_colors[0]}}  # Always include Index with a fixed color

    # Assign colors to the remaining keys dynamically
    color_index = 1
    for key in first_item.keys():
        if key in ('name', 'date', 'number'):  # Custom prioritization of colors
            if key == 'name':
                column_info["Name"] = {'color': 'magenta'}
            elif key == 'date':
                column_info["Date"] = {'color': 'cyan'}
            elif key == 'number':
                column_info["Number"] = {'color': 'yellow'}

        else:
            column_info[key.capitalize()] = {'color': available_colors[color_index % len(available_colors)]}
            color_index += 1
    
    table_show_manager.add_column(column_info)

    # Populate the table with title information
    for i, item in enumerate(generic_obj):
        item_dict = {'Index': str(i)}

        for key in item.keys():
            # Ensure all values are strings for rich add table
            item_dict[key.capitalize()] = str(item[key])

        table_show_manager.add_tv_show(item_dict)

    # Run the table and handle user input
    last_command = table_show_manager.run(force_int_input=True, max_int_input=len(generic_obj))
    table_show_manager.clear()

    # Handle user's quit command
    if last_command == "q":
        Console.print("\n[red]Quit [white]...")
        sys.exit(0)

    # Check if the selected index is within range
    if 0 <= int(last_command) < len(generic_obj):
        return generic_obj[int(last_command)]
    
    else:
        Console.print("\n[red]Wrong index")
        sys.exit(0)


class TheMovieDB:
    def __init__(self, api_key):
        """
        Initialize the class with the API key.
        
        Parameters:
            - api_key (str): The API key for authenticating requests to TheMovieDB.
        """
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.console = Console()
        #self.genres = self._fetch_genres()

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
        genres = self._make_request("genre/movie/list")
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

    def search_movie(self, movie_name: str):
        """
        Search for a movie by name and return its TMDB ID.
        
        Parameters:
            - movie_name (str): The name of the movie to search for.
        
        Returns:
            int: The TMDB ID of the selected movie.
        """
        generic_obj = []
        data = self._make_request("search/movie", {"query": movie_name}).get("results", [])
        if not data:
            self.console.print("No movies found with that name.", style="red")
            return None

        self.console.print("\nSelect a Movie:")
        for i, movie in enumerate(data, start=1):
            generic_obj.append({
                'name': movie['title'],
                'date': movie.get('release_date', 'N/A'),
                'id': movie['id']
            })

        choice = get_select_title(table_show_manager, generic_obj)
        return choice["id"]

    def get_movie_details(self, tmdb_id: int) -> Json_film:
        """
        Fetch and display details for a specific movie using its TMDB ID.

        Parameters:
            - tmdb_id (int): The TMDB ID of the movie.
        
        Returns:
            - Json_film: The movie details as a class.
        """
        movie = self._make_request(f"movie/{tmdb_id}")
        if not movie:
            self.console.print("Movie not found.", style="red")
            return None
        
        return Json_film(movie)

    def search_tv_show(self, tv_name: str):
        """
        Search for a TV show by name and return its TMDB ID.
        
        Parameters:
            - tv_name (str): The name of the TV show to search for.
        
        Returns:
            int: The TMDB ID of the selected TV show.
        """
        data = self._make_request("search/tv", {"query": tv_name}).get("results", [])
        if not data:
            self.console.print("No TV shows found with that name.", style="red")
            return None

        self.console.print("\nSelect a TV Show:")
        for i, show in enumerate(data, start=1):
            self.console.print(f"{i}. {show['name']} (First Air Date: {show.get('first_air_date', 'N/A')})")

        choice = int(input("Enter the number of the show you want: ")) - 1
        selected_show = data[choice]
        return selected_show["id"]  # Return the TMDB ID of the selected TV show

    def get_seasons(self, tv_show_id: int):
        """
        Get seasons for a given TV show.
        
        Parameters:
            - tv_show_id (int): The TMDB ID of the TV show.
        
        Returns:
            int: The season number selected by the user.
        """
        data = self._make_request(f"tv/{tv_show_id}").get("seasons", [])
        if not data:
            self.console.print("No seasons found for this TV show.", style="red")
            return None

        self.console.print("\nSelect a Season:")
        for i, season in enumerate(data, start=1):
            self.console.print(f"{i}. {season['name']} (Episodes: {season['episode_count']})")

        choice = int(input("Enter the number of the season you want: ")) - 1
        return data[choice]["season_number"]

    def get_episodes(self, tv_show_id: int, season_number: int):
        """
        Get episodes for a given season of a TV show.
        
        Parameters:
            - tv_show_id (int): The TMDB ID of the TV show.
            - season_number (int): The season number.
        
        Returns:
            dict: The details of the selected episode.
        """
        data = self._make_request(f"tv/{tv_show_id}/season/{season_number}").get("episodes", [])
        if not data:
            self.console.print("No episodes found for this season.", style="red")
            return None

        self.console.print("\nSelect an Episode:")
        for i, episode in enumerate(data, start=1):
            self.console.print(f"{i}. {episode['name']} (Air Date: {episode.get('air_date', 'N/A')})")

        choice = int(input("Enter the number of the episode you want: ")) - 1
        return data[choice]



# Output
tmdb = TheMovieDB(api_key)


"""
Example:


@ movie
movie_name = "Interstellar"
movie_id = tmdb.search_movie(movie_name)

if movie_id:
    movie_details = tmdb.get_movie_details(tmdb_id=movie_id)
    print(movie_details)


@ series
tv_name = "Game of Thrones"
tv_show_id = tmdb.search_tv_show(tv_name)
if tv_show_id:
    season_number = tmdb.get_seasons(tv_show_id=tv_show_id)
    if season_number:
        episode = tmdb.get_episodes(tv_show_id=tv_show_id, season_number=season_number)
        print(episode)
"""