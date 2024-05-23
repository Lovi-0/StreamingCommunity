# 15.05.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)


# Import
from Src.Lib.Unidecode import transliterate
from Src.Util.file_validator import can_create_file
import unittest


class TestTransliterate(unittest.TestCase):
    def test_transliterate(self):

        # Data test
        string_data = "Il caffè è un'esperienza, così come il gelato."
        expected_result = "Il caffe e un'esperienza, cosi come il gelato."

        # Call the function
        result = transliterate(string_data)

        # Assert
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()