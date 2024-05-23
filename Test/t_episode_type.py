# 15.05.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)


# Import
from Src.Api.Streamingcommunity.Core.Class.EpisodeType import EpisodeManager
import unittest


class TestEpisodeManager(unittest.TestCase):
    def test_get_length(self):
        # Test data
         json_ep_1 = {
            "id":59517,
            "number":1,
            "name":"La Fine",
            "plot":"Okey dokey...",
            "duration":75,
            "scws_id":220399,
            "season_id":3883,
            "created_by":"None",
            "created_at":"2024-04-11T01:31:02.000000Z",
            "updated_at":"2024-04-11T01:31:02.000000Z",
            "images":[
               {
                  "id":103989,
                  "filename":"b7bd00f0-c420-471a-8cc0-1877b3c6182b.webp",
                  "type":"cover",
                  "imageable_type":"episode",
                  "imageable_id":59517,
                  "created_at":"2024-04-11T01:31:02.000000Z",
                  "updated_at":"2024-04-11T01:31:02.000000Z",
                  "original_url_field":"None"
               }
            ]
         }
         json_ep_2 = {'id': 59525, 'number': 2, 'name': "L'obiettivo", 'plot': 'So che quassù non è stato facile per voi', 'duration': 66, 'scws_id': 220404, 'season_id': 3883, 'created_by': None, 'created_at': '2024-04-11T01:38:02.000000Z', 'updated_at': '2024-04-11T01:38:03.000000Z', 'images': [{'id': 103997, 'filename': 'fe838c36-50d0-4096-b4e3-68228c7c9e40.webp', 'type': 'cover', 'imageable_type': 'episode', 'imageable_id': 59525, 'created_at': '2024-04-11T01:38:02.000000Z', 'updated_at': '2024-04-11T01:38:02.000000Z', 'original_url_field': None}]}
         json_ep_3 = {'id': 59531, 'number': 3, 'name': 'La Testa', 'plot': "La Zona Contaminata ha la sua Regola d'Oro...", 'duration': 57, 'scws_id': 220409, 'season_id': 3883, 'created_by': None, 'created_at': '2024-04-11T01:50:02.000000Z', 'updated_at': '2024-04-11T01:50:03.000000Z', 'images': [{'id': 104003, 'filename': 'e0d105aa-01a9-400d-b257-bcd3cddd164c.webp', 'type': 'cover', 'imageable_type': 'episode', 'imageable_id': 59531, 'created_at': '2024-04-11T01:50:02.000000Z', 'updated_at': '2024-04-11T01:50:02.000000Z', 'original_url_field': None}]}


         # Initialize the episode manager
         eps_manager = EpisodeManager()

         # Add episodes to the episode manager
         eps_manager.add_episode(json_ep_1)
         eps_manager.add_episode(json_ep_2)
         eps_manager.add_episode(json_ep_3)

         # Verify if the number of episodes in the episode manager is correct
         self.assertEqual(eps_manager.get_length(), 3)

    def test_add_episode(self):
         # Test data
         json_ep_1 = {
            "id":59517,
            "number":1,
            "name":"La Fine",
            "plot":"Okey dokey...",
            "duration":75,
            "scws_id":220399,
            "season_id":3883,
            "created_by":"None",
            "created_at":"2024-04-11T01:31:02.000000Z",
            "updated_at":"2024-04-11T01:31:02.000000Z",
            "images":[
               {
                  "id":103989,
                  "filename":"b7bd00f0-c420-471a-8cc0-1877b3c6182b.webp",
                  "type":"cover",
                  "imageable_type":"episode",
                  "imageable_id":59517,
                  "created_at":"2024-04-11T01:31:02.000000Z",
                  "updated_at":"2024-04-11T01:31:02.000000Z",
                  "original_url_field":"None"
               }
            ]
         }

         # Initialize the episode manager
         eps_manager = EpisodeManager()

         # Add the episode to the episode manager
         eps_manager.add_episode(json_ep_1)

         # Check the ID of the first episode added
         first_episode_id = eps_manager.episodes[0].id
         self.assertEqual(first_episode_id, json_ep_1['id'])


if __name__ == '__main__':
    unittest.main()