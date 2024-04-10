from Src.Lib.Unidecode import transliterate
from Src.Util.config import config_manager

map_episode = config_manager.get('M3U8_OPTIONS', 'map_episode_name')

def map_episode_title(tv_name: str, episode, number_season: int):
    """
    Maps the episode title to a specific format.
    
    Args:
        tv_name (str): The name of the TV show.
        episode (Episode): The episode object.
        number_season (int): The season number.
        
    Returns:
        str: The mapped episode title.
    """
    global map_episode
    map_episode = map_episode.replace("%(tv_name)", tv_name)
    map_episode = map_episode.replace("%(season)", str(number_season).zfill(2))
    map_episode = map_episode.replace("%(episode)", str(episode.number).zfill(2))
    map_episode = map_episode.replace("%(episode_name)", episode.name)
    return transliterate(map_episode)