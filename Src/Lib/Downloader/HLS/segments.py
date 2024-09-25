# 18.04.24

import os
import sys
import time
import queue
import logging
import binascii
import threading
from queue import PriorityQueue
from urllib.parse import urljoin, urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor


# External libraries
import httpx
from httpx import HTTPTransport
from tqdm import tqdm


# Internal utilities
from Src.Util.console import console
from Src.Util.headers import get_headers, random_headers
from Src.Util.color import Colors
from Src.Util._jsonConfig import config_manager
from Src.Util.os import check_file_existence
from Src.Util.call_stack import get_call_stack


# Logic class
from ...M3U8 import (
    M3U8_Decryption,
    M3U8_Ts_Estimator,
    M3U8_Parser,
    M3U8_UrlFix
)
from .proxyes import main_test_proxy

# Config
TQDM_DELAY_WORKER = config_manager.get_float('M3U8_DOWNLOAD', 'tqdm_delay')
TQDM_USE_LARGE_BAR = config_manager.get_int('M3U8_DOWNLOAD', 'tqdm_use_large_bar')
REQUEST_TIMEOUT = config_manager.get_float('REQUESTS', 'timeout')
REQUEST_MAX_RETRY = config_manager.get_int('REQUESTS', 'max_retry')
REQUEST_VERIFY = config_manager.get_bool('REQUESTS', 'verify_ssl')
THERE_IS_PROXY_LIST = check_file_existence("list_proxy.txt")
PROXY_START_MIN = config_manager.get_float('REQUESTS', 'proxy_start_min')
PROXY_START_MAX = config_manager.get_float('REQUESTS', 'proxy_start_max')


# Variable
headers_index = config_manager.get_dict('REQUESTS', 'user-agent')



class M3U8_Segments:
    def __init__(self, url: str, tmp_folder: str, is_index_url: bool = True):
        """
        Initializes the M3U8_Segments object.

        Parameters:
            - url (str): The URL of the M3U8 playlist.
            - tmp_folder (str): The temporary folder to store downloaded segments.
            - is_index_url (bool): Flag indicating if `m3u8_index` is a URL (default True).
        """
        self.url = url
        self.tmp_folder = tmp_folder
        self.is_index_url = is_index_url
        self.expected_real_time = None 
        
        self.tmp_file_path = os.path.join(self.tmp_folder, "0.ts")
        os.makedirs(self.tmp_folder, exist_ok=True)

        # Util class
        self.decryption: M3U8_Decryption = None 
        self.class_ts_estimator = M3U8_Ts_Estimator(0) 
        self.class_url_fixer = M3U8_UrlFix(url)

        # Sync
        self.queue = PriorityQueue()
        self.stop_event = threading.Event()

        # Server ip
        self.fake_proxy = False

    def add_server_ip(self, list_ip: list):
        """
        Add server IP addresses 

        Args:
            list_ip (list): A list of IP addresses to be added.
        """
        if list_ip is not None:
            self.fake_proxy = True
            self.fake_proxy_ip = list_ip

    def __get_key__(self, m3u8_parser: M3U8_Parser) -> bytes:
        """
        Retrieves the encryption key from the M3U8 playlist.

        Parameters:
            - m3u8_parser (M3U8_Parser): The parser object containing M3U8 playlist information.

        Returns:
            bytes: The encryption key in bytes.
        """
        headers_index = {'user-agent': get_headers()}

        # Construct the full URL of the key
        key_uri = urljoin(self.url, m3u8_parser.keys.get('uri'))
        parsed_url = urlparse(key_uri)
        self.key_base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        logging.info(f"Uri key: {key_uri}")

        # Make request to get porxy
        try:
            response = httpx.get(key_uri, headers=headers_index)
            response.raise_for_status()

        except Exception as e:
            raise Exception(f"Failed to fetch key from {key_uri}: {e}")

        # Convert the content of the response to hexadecimal and then to bytes
        hex_content = binascii.hexlify(response.content).decode('utf-8')
        byte_content = bytes.fromhex(hex_content)
        
        logging.info(f"Key: ('hex': {hex_content}, 'byte': {byte_content})")
        return byte_content
    
    def __gen_proxy__(self, url: str, url_index: int) -> str:
        """
        Change the IP address of the provided URL based on the given index.

        Args:
            - url (str): The original URL that needs its IP address replaced.
            - url_index (int): The index used to select a new IP address from the list of FAKE_PROXY_IP.

        Returns:
            str: The modified URL with the new IP address.
        """
        new_ip_address = self.fake_proxy_ip[url_index % len(self.fake_proxy_ip)]

        # Parse the original URL and replace the hostname with the new IP address
        parsed_url = urlparse(url)._replace(netloc=new_ip_address)  

        return urlunparse(parsed_url)

    def parse_data(self, m3u8_content: str) -> None:
        """
        Parses the M3U8 content to extract segment information.

        Parameters:
            - m3u8_content (str): The content of the M3U8 file.
        """
        m3u8_parser = M3U8_Parser()
        m3u8_parser.parse_data(uri=self.url, raw_content=m3u8_content)

        self.expected_real_time = m3u8_parser.get_duration(return_string=False)
        self.expected_real_time_s = m3u8_parser.duration

        # Check if there is an encryption key in the playlis
        if m3u8_parser.keys is not None:
            try:

                # Extract byte from the key
                key = self.__get_key__(m3u8_parser)
                
            except Exception as e:
                raise Exception(f"Failed to retrieve encryption key {e}.")

            iv = m3u8_parser.keys.get('iv')
            method = m3u8_parser.keys.get('method')

            # Create a decryption object with the key and set the method
            self.decryption = M3U8_Decryption(key, iv, method)

        # Store the segment information parsed from the playlist
        self.segments = m3u8_parser.segments

        # Fix URL if it is incomplete (missing 'http')
        for i in range(len(self.segments)):
            segment_url = self.segments[i]

            if "http" not in segment_url:
                self.segments[i] = self.class_url_fixer.generate_full_url(segment_url)
                logging.info(f"Generated new URL: {self.segments[i]}, from: {segment_url}")

        # Update segments for estimator
        self.class_ts_estimator.total_segments = len(self.segments)
        logging.info(f"Segmnets to download: [{len(self.segments)}]")

        # Proxy
        if THERE_IS_PROXY_LIST:
            console.log("[red]Start validation proxy.")
            self.valid_proxy = main_test_proxy(self.segments[0])
            console.log(f"[cyan]N. Valid ip: [red]{len(self.valid_proxy)}")

            if len(self.valid_proxy) == 0:
                sys.exit(0)

        # Server ip
        if self.fake_proxy:
            for i in range(len(self.segments)):
                segment_url = self.segments[i]
                self.segments[i] = self.__gen_proxy__(segment_url, self.segments.index(segment_url)) 

    def get_info(self) -> None:
        """
        Makes a request to the index M3U8 file to get information about segments.
        """
        headers_index = {'user-agent': get_headers()}

        if self.is_index_url:

            # Send a GET request to retrieve the index M3U8 file
            response = httpx.get(self.url, headers=headers_index)
            response.raise_for_status()

            # Save the M3U8 file to the temporary folder
            if response.status_code == 200:
                path_m3u8_file = os.path.join(self.tmp_folder, "playlist.m3u8")
                open(path_m3u8_file, "w+").write(response.text) 

            # Parse the text from the M3U8 index file
            self.parse_data(response.text)  

        else:

            # Parser data of content of index pass in input to class
            self.parse_data(self.url)  

    def make_requests_stream(self, ts_url: str, index: int, progress_bar: tqdm) -> None:
        """
        Downloads a TS segment and adds it to the segment queue.

        Parameters:
            - ts_url (str): The URL of the TS segment.
            - index (int): The index of the segment.
            - progress_bar (tqdm): Progress counter for tracking download progress.
        """
        need_verify = REQUEST_VERIFY

        # Set to false for only fake proxy that use real ip of server
        if self.fake_proxy:
            need_verify = False

        try:
            start_time = time.time()

            # Make request to get content
            if THERE_IS_PROXY_LIST:

                # Get proxy from list
                proxy = self.valid_proxy[index % len(self.valid_proxy)]
                logging.info(f"Use proxy: {proxy}")

                with httpx.Client(proxies=proxy, verify=need_verify) as client:  
                    if 'key_base_url' in self.__dict__:
                        response = client.get(ts_url, headers=random_headers(self.key_base_url), timeout=REQUEST_TIMEOUT, follow_redirects=True)
                    else:
                        response = client.get(ts_url, headers={'user-agent': get_headers()}, timeout=REQUEST_TIMEOUT, follow_redirects=True)

            else:
                with httpx.Client(verify=need_verify) as client_2:
                    if 'key_base_url' in self.__dict__:
                        response = client_2.get(ts_url, headers=random_headers(self.key_base_url), timeout=REQUEST_TIMEOUT, follow_redirects=True)
                    else:
                        response = client_2.get(ts_url, headers={'user-agent': get_headers()}, timeout=REQUEST_TIMEOUT, follow_redirects=True)

            # Get response content
            response.raise_for_status()
            duration = time.time() - start_time
            segment_content = response.content

            # Update bar
            response_size = int(response.headers.get('Content-Length', 0))

            if response_size == 0:
                response_size = int(len(response.content))

            # Update progress bar with custom Class
            self.class_ts_estimator.update_progress_bar(response_size, duration, progress_bar)

            # Decrypt the segment content if decryption is needed
            if self.decryption is not None:
                segment_content = self.decryption.decrypt(segment_content)

            # Add the segment to the queue
            self.queue.put((index, segment_content))
            progress_bar.update(1)

        except Exception as e:
            console.print(f"Failed download: '{ts_url}' with error: {e}")

    def write_segments_to_file(self):
        """
        Writes downloaded segments to a file in the correct order.
        """
        with open(self.tmp_file_path, 'wb') as f:
            expected_index = 0
            buffer = {}

            while not self.stop_event.is_set() or not self.queue.empty():
                try:
                    index, segment_content = self.queue.get(timeout=1)

                    if index == expected_index:
                        f.write(segment_content)
                        f.flush()
                        expected_index += 1

                        # Write any buffered segments in order
                        while expected_index in buffer:
                            f.write(buffer.pop(expected_index))
                            f.flush()
                            expected_index += 1
                    else:
                        buffer[index] = segment_content

                except queue.Empty:
                    continue

    def download_streams(self, add_desc):
        """
        Downloads all TS segments in parallel and writes them to a file.

        Parameters:
            - add_desc (str): Additional description for the progress bar.
        """

        # Get config site from prev stack
        frames = get_call_stack()
        logging.info(f"Extract info from: {frames}")
        config_site = str(frames[-4]['folder_base'])
        logging.info(f"Use frame: {frames[-1]}")

        # Workers to use for downloading
        TQDM_MAX_WORKER = 0

        # Select audio workers from folder of frames stack prev call.
        try:
            VIDEO_WORKERS = int(config_manager.get_dict('SITE', config_site)['video_workers'])
            if VIDEO_WORKERS == -1: VIDEO_WORKERS = os.cpu_count()
        except:
            VIDEO_WORKERS = os.cpu_count()

        try:
            AUDIO_WORKERS = int(config_manager.get_dict('SITE', config_site)['audio_workers'])
            if AUDIO_WORKERS == -1: AUDIO_WORKERS = os.cpu_count()
        except:
            AUDIO_WORKERS = os.cpu_count()

        # Differnt workers for audio and video
        if "video" in str(add_desc):
            TQDM_MAX_WORKER = VIDEO_WORKERS
        if "audio" in str(add_desc):
            TQDM_MAX_WORKER = AUDIO_WORKERS

        # Custom bar for mobile and pc
        if TQDM_USE_LARGE_BAR:
            bar_format = (
                f"{Colors.YELLOW}[HLS] {Colors.WHITE}({Colors.CYAN}{add_desc}{Colors.WHITE}): "
                f"{Colors.RED}{{percentage:.2f}}% "
                f"{Colors.MAGENTA}{{bar}} "
                f"{Colors.WHITE}[ {Colors.YELLOW}{{n_fmt}}{Colors.WHITE} / {Colors.RED}{{total_fmt}} {Colors.WHITE}] "
                f"{Colors.YELLOW}{{elapsed}} {Colors.WHITE}< {Colors.CYAN}{{remaining}}{{postfix}} {Colors.WHITE}]"
            )
        else:
            bar_format = (
                f"{Colors.YELLOW}Proc{Colors.WHITE}: "
                f"{Colors.RED}{{percentage:.2f}}% "
                f"{Colors.WHITE}| "
                f"{Colors.CYAN}{{remaining}}{{postfix}} {Colors.WHITE}]"
            )

        # Create progress bar
        progress_bar = tqdm(
            total=len(self.segments), 
            unit='s',
            ascii='░▒█',
            bar_format=bar_format,
            mininterval=0.05
        )

        # Start a separate thread to write segments to the file
        writer_thread = threading.Thread(target=self.write_segments_to_file)
        writer_thread.start()

        # Ff proxy avaiable set max_workers to number of proxy
        # else set max_workers to TQDM_MAX_WORKER
        max_workers = len(self.valid_proxy) if THERE_IS_PROXY_LIST else TQDM_MAX_WORKER

        # if proxy avaiable set timeout to variable time
        # else set timeout to TDQM_DELAY_WORKER
        if THERE_IS_PROXY_LIST:
            num_proxies = len(self.valid_proxy)
            self.working_proxy_list = self.valid_proxy

            if num_proxies > 0:
                # calculate delay based on number of proxies
                # dalay should be between 0.5 and 1
                delay = max(PROXY_START_MIN, min(PROXY_START_MAX, 1 / (num_proxies + 1)))
            else:
                delay = TQDM_DELAY_WORKER
        else:
            delay = TQDM_DELAY_WORKER

        # Start all workers
        logging.info(f"Worker to use: {max_workers}")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for index, segment_url in enumerate(self.segments):
                time.sleep(delay)
                executor.submit(self.make_requests_stream, segment_url, index, progress_bar)

        # Wait for all tasks to complete
        executor.shutdown(wait=True)
        self.stop_event.set()
        writer_thread.join()
        progress_bar.close()
