# 18.04.24

import os
import sys
import time
import queue
import threading
import logging
import binascii
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse, urlunparse


# External libraries
from Src.Lib.Request import requests
from tqdm import tqdm


# Internal utilities
from Src.Util.console import console
from Src.Util.headers import get_headers
from Src.Util.color import Colors
from Src.Util._jsonConfig import config_manager

# Logic class
from ..M3U8 import (
    M3U8_Decryption,
    M3U8_Ts_Estimator,
    M3U8_Parser,
    M3U8_UrlFix
)

# Config
TQDM_MAX_WORKER = config_manager.get_int('M3U8_DOWNLOAD', 'tdqm_workers')
TQDM_USE_LARGE_BAR = config_manager.get_int('M3U8_DOWNLOAD', 'tqdm_use_large_bar')
REQUEST_VERIFY_SSL = config_manager.get_bool('REQUESTS', 'verify_ssl')


# Variable
headers_index = config_manager.get_dict('REQUESTS', 'index')
headers_segments = config_manager.get_dict('REQUESTS', 'segments')



class M3U8_Segments:
    def __init__(self, url: str, tmp_folder: str):
        """
        Initializes the M3U8_Segments object.

        Args:
            - url (str): The URL of the M3U8 playlist.
            - tmp_folder (str): The temporary folder to store downloaded segments.
        """
        self.url = url
        self.fake_proxy = False
        self.tmp_folder = tmp_folder
        self.tmp_file_path = os.path.join(self.tmp_folder, "0.ts")
        os.makedirs(self.tmp_folder, exist_ok=True)

        # Util class
        self.decryption: M3U8_Decryption = None 
        self.class_ts_estimator = M3U8_Ts_Estimator(0) 
        self.class_url_fixer = M3U8_UrlFix(url)

        # Sync
        self.current_index = 0                                      # Index of the current segment to be written
        self.segment_queue = queue.PriorityQueue()                  # Priority queue to maintain the order of segments
        self.condition = threading.Condition()                      # Condition variable for thread synchronization

    def add_server_ip(self, list_ip):
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

        Args:
            - m3u8_parser (M3U8_Parser): The parser object containing M3U8 playlist information.

        Returns:
            bytes: The encryption key in bytes.
        """
        headers_index['user-agent'] = get_headers()


        # Construct the full URL of the key
        key_uri = urljoin(self.url, m3u8_parser.keys.get('uri'))  
        logging.info(f"Uri key: {key_uri}")

        try:
            response = requests.get(key_uri, headers=headers_index)
            response.raise_for_status()

        except Exception as e:
            raise Exception(f"Failed to fetch key from {key_uri}: {e}")

        # Convert the content of the response to hexadecimal and then to bytes
        hex_content = binascii.hexlify(response.content).decode('utf-8')
        byte_content = bytes.fromhex(hex_content)
        
        logging.info(f"Key: ('hex': {hex_content}, 'byte': {byte_content})")
        return byte_content

    def __test_ip(self, url_to_test: str):
        """
        Tests each proxy IP by sending a request to a corresponding segment URL.
        """

        failed_ips = []

        for i in range(len(self.fake_proxy_ip)):

            try:
                response = requests.get(url_to_test, verify=False, retries=0)

                if response == None:
                    logging.error(f"[Work] to make request using: {url_to_test}")
                    failed_ips.append(i)

            except:

                # Log the error and add the IP to the list of failed IPs
                logging.error(f"[Fail] to make request using IP in this request: {url_to_test}")
                failed_ips.append(i)

        # Remove the failed IPs from the fake_proxy_ip list
        self.fake_proxy_ip = [ip for j, ip in enumerate(self.fake_proxy_ip) if j not in failed_ips]

        # Exit the program if 50% requests failed
        if len(failed_ips) / 2 > len(self.fake_proxy_ip):
            logging.error("All requests with ip failed.")
            
            # Set to not use proxy
            self.fake_proxy_ip = None
            self.fake_proxy = False

            return False

    def parse_data(self, m3u8_content: str) -> None:
        """
        Parses the M3U8 content to extract segment information.

        Args:
            - m3u8_content (str): The content of the M3U8 file.
        """
        m3u8_parser = M3U8_Parser()
        m3u8_parser.parse_data(uri=self.url, raw_content=m3u8_content)

        console.log(f"[red]Expected duration after download: {m3u8_parser.get_duration()}")
        console.log(f"[red]There is key: [yellow]{m3u8_parser.keys is not None}")

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

        # Change IP address of server
        if self.fake_proxy:
            for i in range(len(self.segments)):
                segment_url = self.segments[i]

                # Set to not use proxy if 50% failed
                if not self.__test_ip(segment_url):
                    console.log("[red]Cant use proxy switch to normal url.")
                    self.fake_proxy = False
                    break

                self.segments[i] = self.__gen_proxy__(segment_url, self.segments.index(segment_url)) 

        # Save new playlist of segment
        path_m3u8_file = os.path.join(self.tmp_folder, "playlist_fix.m3u8")
        with open(path_m3u8_file, "w") as file:
            for item in self.segments:
                file.write(f"{item}\n")

        # Update segments for estimator
        self.class_ts_estimator.total_segments = len(self.segments)
        logging.info(f"Segmnets to donwload: [{len(self.segments)}]")

    def get_info(self) -> None:
        """
        Makes a request to the index M3U8 file to get information about segments.
        """
        headers_index['user-agent'] = get_headers()

        # Send a GET request to retrieve the index M3U8 file
        response = requests.get(self.url, headers=headers_index)
        response.raise_for_status()

        # Save the M3U8 file to the temporary folder
        if response.ok:
            path_m3u8_file = os.path.join(self.tmp_folder, "playlist.m3u8")
            open(path_m3u8_file, "w+").write(response.text) 

        # Parse the text from the M3U8 index file
        self.parse_data(response.text)  

    def __gen_proxy__(self, url: str, url_index: int) -> str:
        """
        Change the IP address of the provided URL based on the given index.

        Args:
            - url (str): The original URL that needs its IP address replaced.
            - url_index (int): The index used to select a new IP address from the list of FAKE_PROXY_IP.

        Returns:
            str: The modified URL with the new IP address.
        """
        if self.fake_proxy:

            new_ip_address = self.fake_proxy_ip[url_index % len(self.fake_proxy_ip)]

            # Parse the original URL and replace the hostname with the new IP address
            parsed_url = urlparse(url)._replace(netloc=new_ip_address)  

            return urlunparse(parsed_url)
        
        else:
            return url

    def make_requests_stream(self, ts_url: str, index: int, progress_bar: tqdm) -> None:
        """
        Downloads a TS segment and adds it to the segment queue.

        Args:
            - ts_url (str): The URL of the TS segment.
            - index (int): The index of the segment.
            - progress_bar (tqdm): Progress counter for tracking download progress.
        """

        # Generate new user agent
        headers_segments['user-agent'] = get_headers()

        try:

            # Make request and calculate time duration
            start_time = time.time()
            response = requests.get(ts_url, headers=headers_segments, verify=REQUEST_VERIFY_SSL, timeout=30)
            duration = time.time() - start_time
            logging.info(f"Make request to get segment: [{index} - {len(self.segments)}] in: {duration}, len data: {len(response.content)}")

            if response.ok:

                # Get the content of the segment
                segment_content = response.content

                # Update bar
                self.class_ts_estimator.update_progress_bar(segment_content, duration, progress_bar)

                # Decrypt the segment content if decryption is needed
                if self.decryption is not None:
                    segment_content = self.decryption.decrypt(segment_content)

                with self.condition:
                    self.segment_queue.put((index, segment_content))    # Add the segment to the queue
                    self.condition.notify()                             # Notify the writer thread that a new segment is available
            else:
                logging.error(f"Failed to download segment: {ts_url}")

        except Exception as e:
            logging.error(f"Exception while downloading segment: {e}")

        # Update bar
        progress_bar.update(1)

    def write_segments_to_file(self):
        """
        Writes downloaded segments to a file in the correct order.
        """
        with open(self.tmp_file_path, 'ab') as f:
            while True:
                with self.condition:
                    while self.segment_queue.empty() and self.current_index < len(self.segments):
                        self.condition.wait()                                           # Wait until a new segment is available or all segments are downloaded

                    if self.segment_queue.empty() and self.current_index >= len(self.segments):
                        break                                                           # Exit loop if all segments have been processed

                    if not self.segment_queue.empty():
                        # Get the segment from the queue
                        index, segment_content = self.segment_queue.get()

                        # Write the segment to the file
                        if index == self.current_index:
                            f.write(segment_content)
                            self.current_index += 1
                            self.segment_queue.task_done()
                        else:
                            self.segment_queue.put((index, segment_content))            # Requeue the segment if it is not the next to be written
                            self.condition.notify()

    def download_streams(self, add_desc):
        """
        Downloads all TS segments in parallel and writes them to a file.

        Args:
            - add_desc (str): Additional description for the progress bar.
        """
        if TQDM_USE_LARGE_BAR:
            bar_format=f"{Colors.YELLOW}Downloading {Colors.WHITE}({add_desc}{Colors.WHITE}): {Colors.RED}{{percentage:.2f}}% {Colors.MAGENTA}{{bar}} {Colors.WHITE}| {Colors.YELLOW}{{n_fmt}}{Colors.WHITE} / {Colors.RED}{{total_fmt}} {Colors.WHITE}| {Colors.YELLOW}{{elapsed}} {Colors.WHITE}< {Colors.CYAN}{{remaining}}{{postfix}} {Colors.WHITE}]"
        else:
            bar_format=f"{Colors.YELLOW}Proc{Colors.WHITE}: {Colors.RED}{{percentage:.2f}}% {Colors.WHITE}| {Colors.CYAN}{{remaining}}{{postfix}} {Colors.WHITE}]"
            
        progress_bar = tqdm(
            total=len(self.segments), 
            unit='s',
            ascii='░▒█',
            bar_format=bar_format
        )

        with ThreadPoolExecutor(max_workers=TQDM_MAX_WORKER) as executor:

            # Start a separate thread to write segments to the file
            writer_thread = threading.Thread(target=self.write_segments_to_file)
            writer_thread.start()

            # Start all workers
            for index, segment_url in enumerate(self.segments):

                # Submit the download task to the executor
                executor.submit(self.make_requests_stream, segment_url, index, progress_bar)

            # Wait for all segments to be downloaded
            executor.shutdown()

            with self.condition:
                self.condition.notify_all()     # Wake up the writer thread if it's waiting
            writer_thread.join()                # Wait for the writer thread to finish
