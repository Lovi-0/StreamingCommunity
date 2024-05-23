# 24.03.24

import random
import uuid


# Internal logic
from Src.Util._jsonConfig import config_manager
from Src.Lib.UserAgent import ua


def get_headers(profile_name):

    return {
        'accept': '*/*',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'referer': f'https://www.instagram.com/{profile_name}/',
        'x-ig-app-id': '936619743392459',
        'user-agent': ua.get_random_user_agent('chrome')
    }


def get_cookies():

    return {
        'sessionid': config_manager.get('DEFAULT', 'instagram_session')
    }