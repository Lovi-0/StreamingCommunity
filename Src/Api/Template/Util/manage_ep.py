# 19.06.24

import sys
import logging

from typing import List


# Internal utilities
from Src.Util._jsonConfig import config_manager
from Src.Util.os import remove_special_characters


# Config
MAP_EPISODE = config_manager.get('DEFAULT', 'map_episode_name')


def dynamic_format_number(n: int) -> str:
    """
    Formats a number by adding a leading zero if it is less than 9.
    The width of the resulting string is dynamic, calculated as the number of digits in the number plus one 
    for numbers less than 9, otherwise the width remains the same.
    
    Parameters:
        - n (int): The number to format.
    
    Returns:
        - str: The formatted number as a string with a leading zero if the number is less than 9.
    """
    if n < 10:
        width = len(str(n)) + 1
    else:
        width = len(str(n))

    return str(n).zfill(width)


def manage_selection(cmd_insert: str, max_count: int) -> List[int]:
    """
    Manage user selection for seasons to download.

    Parameters:
        - cmd_insert (str): User input for season selection.
        - max_count (int): Maximum count of seasons available.

    Returns:
        list_season_select (List[int]): List of selected seasons.
    """
    list_season_select = []
    logging.info(f"Command insert: {cmd_insert}, end index: {max_count + 1}")

    # For a single number (e.g., '5')
    if cmd_insert.isnumeric():
        list_season_select.append(int(cmd_insert))

    # For a range (e.g., '[5-12]')
    elif "[" in cmd_insert:

        # Extract the start and end parts
        start, end = map(str.strip, cmd_insert[1:-1].split('-'))
        start = int(start)

        # If end is an integer, convert it
        try:
            end = int(end)

        except ValueError:
            # end remains a string if conversion fails
            pass

        # Generate the list_season_select based on the type of end
        if isinstance(end, int):
            list_season_select = list(range(start, end + 1))

        elif end == "*":
            list_season_select = list(range(start, max_count + 1))

        else:
            raise ValueError("Invalid end value")
        
    # For all seasons
    elif cmd_insert == "*":
        list_season_select = list(range(1, max_count+1))

    # Return list of selected seasons)
    logging.info(f"List return: {list_season_select}")
    return list_season_select


def map_episode_title(tv_name: str, number_season: int, episode_number: int, episode_name: str) -> str:
    """
    Maps the episode title to a specific format.

    Parameters:
        tv_name (str): The name of the TV show.
        number_season (int): The season number.
        episode_number (int): The episode number.
        episode_name (str): The original name of the episode.

    Returns:
        str: The mapped episode title.
    """
    map_episode_temp = MAP_EPISODE
    map_episode_temp = map_episode_temp.replace("%(tv_name)", remove_special_characters(tv_name))
    map_episode_temp = map_episode_temp.replace("%(season)", dynamic_format_number(number_season))
    map_episode_temp = map_episode_temp.replace("%(episode)", dynamic_format_number(episode_number))
    map_episode_temp = map_episode_temp.replace("%(episode_name)", remove_special_characters(episode_name))

    # Additional fix
    map_episode_temp = map_episode_temp.replace(".", "_")

    logging.info(f"Map episode string return: {map_episode_temp}")
    return map_episode_temp
