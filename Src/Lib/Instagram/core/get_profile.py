# 24.03.24

import logging


# External utilities
from Src.Lib.Request import requests


# Internal utilities
from ._util import get_headers, get_cookies
from ..model import InstaProfile


def get_data(profile_name) -> InstaProfile:

    # Prepare url
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={profile_name}"

    # Get response from request
    response = requests.get(url, headers=get_headers(profile_name), cookies=get_cookies())

    if response.ok:

        # Get json response
        data_json = response.json()

        if data_json is not None:

            # Parse json
            obj_InstaProfile = InstaProfile(data_json)

            return obj_InstaProfile
        
        else:
            logging.error(f"Cant fetch data for this profile: {profile_name}, empty json response.")
    
    else:
        logging.error(f"Cant fetch data for this profile: {profile_name}.")

