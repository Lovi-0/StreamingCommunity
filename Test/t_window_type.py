# 15.05.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)


# Import
from Src.Api.Streamingcommunity.Core.Class.WindowType import WindowVideo, WindowParameter
import unittest


class TestWindowVideo(unittest.TestCase):
    def test_str(self):
        # Test data
        json_video = {'id': 220399, 'name': 'Fallout S:1 E:1', 'filename': 'Fallout.S01E01.La.Fine.1080p.AMZN.WEB-DL.ITA.ENG.DDP5.1.H.264.mkv', 'size': 5250906, 'quality': 1080, 'duration': 4498, 'views': 0, 'is_viewable': 1, 'status': 'public', 'fps': 24, 'legacy': 0, 'folder_id': '81aff513-a0c4-4723-bacc-fca2d1143eb5', 'created_at_diff': '3 settimane fa'}
        expected_output = "WindowVideo(id=220399, name='Fallout S:1 E:1', filename='Fallout.S01E01.La.Fine.1080p.AMZN.WEB-DL.ITA.ENG.DDP5.1.H.264.mkv', size='5250906', quality='1080', duration='4498', views=0, is_viewable=1, status='public', fps=24, legacy=0, folder_id=81aff513-a0c4-4723-bacc-fca2d1143eb5, created_at_diff='3 settimane fa')"

        # Initialize WindowVideo object
        win_video = WindowVideo(json_video)

        # Assert
        self.assertEqual(str(win_video), expected_output)

class TestWindowParameter(unittest.TestCase):
    def test_str(self):
        # Test data
        json_parameter = {'token': 'cWDn4XKemoNr7PnPghud2Q', 'token360p': '', 'token480p': 'arPfGVKQ7Dk7wh9xJ8QJDA', 'token720p': 'fuEf67Z1WuD-OgWzS7OxxA', 'token1080p': '3O-DrtT7I3ZmecYQgpC45A', 'expires': '1720094851'}
        expected_output = "WindowParameter(token='cWDn4XKemoNr7PnPghud2Q', token360p='', token480p='arPfGVKQ7Dk7wh9xJ8QJDA', token720p='fuEf67Z1WuD-OgWzS7OxxA', token1080p='3O-DrtT7I3ZmecYQgpC45A', expires='1720094851')"

        # Initialize WindowParameter object
        win_par = WindowParameter(json_parameter)

        # Assert
        self.assertEqual(str(win_par), expected_output)

        
if __name__ == '__main__':
    unittest.main()