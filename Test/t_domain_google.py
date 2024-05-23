# 15.05.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)


# Import
from Src.Api.Streamingcommunity.Core.Util.get_domain import grab_sc_top_level_domain
from Src.Api.Animeunity.Core.Util.get_domain import grab_au_top_level_domain
import unittest
import time
import logging


class URLFilter(logging.Filter):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def filter(self, record):
        return self.url not in record.getMessage()
    

# Configure logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # Set logger level to ERROR


# Add custom filter to suppress URLs
url_filters = ['https://streamingcommunity', 'https://www.animeunity']
for url in url_filters:
    logger.addFilter(URLFilter(url))


# Variable
real_stream_domain = "foo"
real_anime_domain = "to"



class TestGrabStreamingDomain(unittest.TestCase):
    def test_light_streaming(self):
        start = time.time()
        result = grab_sc_top_level_domain(method='light')
        end = time.time()
        print(f"Light streaming: {result}, in: {end - start}")

        # Assert that result is as expected
        self.assertEqual(result, real_stream_domain)

    def test_strong_streaming(self):
        start = time.time()
        result = grab_sc_top_level_domain(method='strong')
        end = time.time()
        print(f"Strong streaming: {result}, in: {end - start}")

        # Assert that result is as expected
        self.assertEqual(result, real_stream_domain)

    def test_light_anime(self):
        start = time.time()
        result = grab_au_top_level_domain(method='light')
        end = time.time()
        print(f"Light anime: {result}, in: {end - start}")

        # Assert that result is as expected
        self.assertEqual(result, real_anime_domain)

    def test_strong_anime(self):
        start = time.time()
        result = grab_au_top_level_domain(method='strong')
        end = time.time()
        print(f"Strong anime: {result}, in: {end - start}")

        # Assert that result is as expected
        self.assertEqual(result, real_anime_domain)

if __name__ == '__main__':
    unittest.main()

