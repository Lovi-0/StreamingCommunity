# 19.06.24

import logging
from typing import List


# Internal utilities
from StreamingCommunity.Src.Util._jsonConfig import config_manager
from StreamingCommunity.Src.Util.os import os_manager


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
    Manage user selection for seasons or episodes to download.

    Parameters:
        - cmd_insert (str): User input for selection.
        - max_count (int): Maximum count available.

    Returns:
        list_selection (List[int]): List of selected items.
    """
    list_selection = []
    logging.info(f"Command insert: {cmd_insert}, end index: {max_count + 1}")

    # For a single number (e.g., '5')
    if cmd_insert.isnumeric():
        list_selection.append(int(cmd_insert))

    # For a range (e.g., '5-12')
    elif "-" in cmd_insert:
        start, end = map(str.strip, cmd_insert.split('-'))
        start = int(start)
        end = int(end) if end.isnumeric() else max_count

        list_selection = list(range(start, end + 1))
        
    # For all items ('*')
    elif cmd_insert == "*":
        list_selection = list(range(1, max_count + 1))

    else:
        raise ValueError("Invalid input format")

    logging.info(f"List return: {list_selection}")
    return list_selection


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
    
    if tv_name != None:
        map_episode_temp = map_episode_temp.replace("%(tv_name)", os_manager.get_sanitize_file(tv_name))

    if number_season != None:
        map_episode_temp = map_episode_temp.replace("%(season)", dynamic_format_number(number_season))
    else:
        map_episode_temp = map_episode_temp.replace("%(season)", dynamic_format_number(0))

    if episode_number != None:
        map_episode_temp = map_episode_temp.replace("%(episode)", dynamic_format_number(episode_number))
    else:
        map_episode_temp = map_episode_temp.replace("%(episode)", dynamic_format_number(0))

    if episode_name != None:
        map_episode_temp = map_episode_temp.replace("%(episode_name)", os_manager.get_sanitize_file(episode_name))

    logging.info(f"Map episode string return: {map_episode_temp}")
    return map_episode_temp


# --> for season
def validate_selection(list_season_select: List[int], seasons_count: int) -> List[int]:
    """
    Validates and adjusts the selected seasons based on the available seasons.

    Parameters:
        - list_season_select (List[int]): List of seasons selected by the user.
        - seasons_count (int): Total number of available seasons.

    Returns:
        - List[int]: Adjusted list of valid season numbers.
    """

    # Remove any seasons greater than the available seasons
    valid_seasons = [season for season in list_season_select if 1 <= season <= seasons_count]

    # If the list is empty, the input was completely invalid
    if not valid_seasons:
        print()
        raise ValueError(f"Invalid selection: The selected seasons are outside the available range (1-{seasons_count}).")

    return valid_seasons


# --> for episode
def validate_episode_selection(list_episode_select: List[int], episodes_count: int) -> List[int]:
    """
    Validates and adjusts the selected episodes based on the available episodes.

    Parameters:
        - list_episode_select (List[int]): List of episodes selected by the user.
        - episodes_count (int): Total number of available episodes in the season.

    Returns:
        - List[int]: Adjusted list of valid episode numbers.
    """

    # Remove any episodes greater than the available episodes
    valid_episodes = [episode for episode in list_episode_select if 1 <= episode <= episodes_count]

    # If the list is empty, the input was completely invalid
    if not valid_episodes:
        print()
        raise ValueError(f"Invalid selection: The selected episodes are outside the available range (1-{episodes_count}).")

    return valid_episodes
