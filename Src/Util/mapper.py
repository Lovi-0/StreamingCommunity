# 10.04.24

from unidecode import unidecode as transliterate


# Internal utilities
from Src.Util.config import config_manager
from Src.Api.Class.EpisodeType import Episode


# Config
map_episode = config_manager.get('M3U8_OPTIONS', 'map_episode_name')


def map_episode_title(tv_name: str, episode: Episode, number_season: int):
    """
    Maps the episode title to a specific format.
    
    Args:
        tv_name (str): The name of the TV show.
        episode (Episode): The episode object.
        number_season (int): The season number.
        
    Returns:
        str: The mapped episode title.
    """

    map_episode_temp = map_episode
    map_episode_temp = map_episode_temp.replace("%(tv_name)", tv_name)
    map_episode_temp = map_episode_temp.replace("%(season)", str(number_season).zfill(2))
    map_episode_temp = map_episode_temp.replace("%(episode)", str(episode.number).zfill(2))
    map_episode_temp = map_episode_temp.replace("%(episode_name)", episode.name)

    return transliterate(map_episode_temp)