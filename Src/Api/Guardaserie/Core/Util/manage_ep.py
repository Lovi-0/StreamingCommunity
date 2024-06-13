# 02.05.24

import logging

from typing import List


# Internal utilities
from Src.Util._jsonConfig import config_manager


# Config
MAP_EPISODE = config_manager.get('DEFAULT', 'map_episode_name')


def manage_selection(cmd_insert: str, max_count: int) -> List[int]:
    """
    Manage user selection for seasons to download.

    Args:
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
        start, end = map(int, cmd_insert[1:-1].split('-'))
        list_season_select = list(range(start, end + 1))

    # For all seasons
    elif cmd_insert == "*":
        list_season_select = list(range(1, max_count+1))

    # Return list of selected seasons)
    logging.info(f"List return: {list_season_select}")
    return list_season_select


