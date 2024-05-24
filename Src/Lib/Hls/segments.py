# 18.04.24

import os
import sys
import time
import queue
import threading
import signal
import logging
import binascii
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse, urlunparse


# External libraries
from tqdm import tqdm


# Internal utilities
from Src.Util.console import console
from Src.Util.headers import get_headers
from Src.Util.color import Colors
from Src.Lib.Request.my_requests import requests
from Src.Util._jsonConfig import config_manager
from Src.Util.os import ( 
    format_size
)


# Logic class
from ..M3U8 import (
    M3U8_Decryption,
    M3U8_Ts_Files,
    M3U8_Parser,
    m3u8_url_fix
)


# Config
TQDM_MAX_WORKER = config_manager.get_int('M3U8', 'tdqm_workers')
DELAY_START_WORKER = config_manager.get_float('M3U8', 'delay_start_workers')
TQDM_PROGRESS_TIMEOUT = config_manager.get_int('M3U8', 'tqdm_progress_timeout')
REQUESTS_TIMEOUT = config_manager.get_int('M3U8', 'requests_timeout')
ENABLE_TIME_TIMEOUT = config_manager.get_bool('M3U8', 'enable_time_quit')
TQDM_SHOW_PROGRESS = config_manager.get_bool('M3U8', 'tqdm_show_progress')
LIMIT_DONWLOAD_PERCENTAGE = config_manager.get_float('M3U8', 'download_percentage')
SAVE_M3U8_FILE = config_manager.get_float('M3U8', 'save_m3u8_content')
FAKE_PROXY = config_manager.get_float('M3U8', 'fake_proxy')
FAKE_PROXY_IP = config_manager.get_list('M3U8', 'fake_proxy_ip')


# Variable
headers_index = config_manager.get_dict('M3U8_REQUESTS', 'index')
headers_segments = config_manager.get_dict('M3U8_REQUESTS', 'segments')



class M3U8_Segments:
    def __init__(self, url: str, tmp_folder: str):
        """
        Initializes the M3U8_Segments object.

        Args:
            - url (str): The URL of the M3U8 playlist.
            - tmp_folder (str): The temporary folder to store downloaded segments.
        """
        self.url = url
        self.tmp_folder = tmp_folder
        self.downloaded_size = 0
        self.decryption: M3U8_Decryption = None                     # Initialize decryption as None
        self.class_ts_files_size = M3U8_Ts_Files()                  # Initialize the TS files size class
        self.segment_queue = queue.PriorityQueue()                  # Priority queue to maintain the order of segments
        self.current_index = 0                                      # Index of the current segment to be written
        self.tmp_file_path = os.path.join(self.tmp_folder, "0.ts")  # Path to the temporary file
        self.condition = threading.Condition()                      # Condition variable for thread synchronization
        self.ctrl_c_detected = False                                # Global variable to track Ctrl+C detection

        os.makedirs(self.tmp_folder, exist_ok=True)                 # Create the temporary folder if it does not exist
        self.list_speeds = []
        self.average_over = int(TQDM_MAX_WORKER / 3)

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

            # Send HTTP GET request to fetch the key
            response = requests.get(key_uri, headers=headers_index)
            response.raise_for_status()

        except Exception as e:
            raise Exception(f"Failed to fetch key from {key_uri}: {e}")

        # Convert the content of the response to hexadecimal and then to bytes
        hex_content = binascii.hexlify(response.content).decode('utf-8')
        byte_content = bytes.fromhex(hex_content)
        
        logging.info(f"Key: ('hex': {hex_content}, 'byte': {byte_content})")
        return byte_content

    def parse_data(self, m3u8_content: str) -> None:
        """
        Parses the M3U8 content to extract segment information.

        Args:
            - m3u8_content (str): The content of the M3U8 file.
        """
        m3u8_parser = M3U8_Parser()
        m3u8_parser.parse_data(uri=self.url, raw_content=m3u8_content)  # Parse the content of the M3U8 playlist

        console.log(f"[cyan]There is key: [yellow]{m3u8_parser.keys is not None}")

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

    def get_info(self) -> None:
        """
        Makes a request to the index M3U8 file to get information about segments.
        """
        headers_index['user-agent'] = get_headers()

        # Send a GET request to retrieve the index M3U8 file
        response = requests.get(self.url, headers=headers_index)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the M3U8 file to the temporary folder
        if SAVE_M3U8_FILE:
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
        new_ip_address = FAKE_PROXY_IP[url_index % len(FAKE_PROXY_IP)]

        # Parse the original URL and replace the hostname with the new IP address
        parsed_url = urlparse(url)._replace(netloc=new_ip_address)  
        return urlunparse(parsed_url)

    def make_requests_stream(self, ts_url: str, index: int, stop_event: threading.Event, progress_counter: tqdm, add_desc: str) -> None:
        """
        Downloads a TS segment and adds it to the segment queue.

        Args:
            - ts_url (str): The URL of the TS segment.
            - index (int): The index of the segment.
            - stop_event (threading.Event): Event to signal the stop of downloading.
            - progress_counter (tqdm): Progress counter for tracking download progress.
            - add_desc (str): Additional description for the progress bar.
        """

        if stop_event.is_set():
            return  # Exit if the stop event is set
        
        headers_segments['user-agent'] = get_headers()

        # Fix URL if it is incomplete (missing 'http')
        if "http" not in ts_url:
            ts_url = m3u8_url_fix.generate_full_url(ts_url)
            logging.info(f"Generated new URL: {ts_url}")

        try:

            # Change IP address if FAKE_PROXY is enabled
            if FAKE_PROXY:
                ts_url = self.__gen_proxy__(ts_url, self.segments.index(ts_url)) 

            # Make request and calculate time duration
            start_time = time.time()
            response = requests.get(ts_url, headers=headers_segments, timeout=REQUESTS_TIMEOUT, verify_ssl=False)  # Send GET request for the segment
            duration = time.time() - start_time
            
            if response.ok:

                # Get the content of the segment
                segment_content = response.content
                total_downloaded = len(response.content)

                # Calculate mbps 
                speed_mbps = (total_downloaded * 8) / (duration * 1_000_000)  * TQDM_MAX_WORKER
                self.list_speeds.append(speed_mbps)

                # Get average speed after (average_over)
                if len(self.list_speeds) > self.average_over:
                    self.list_speeds.pop(0)
                average_speed = ( sum(self.list_speeds) / len(self.list_speeds) ) / 10 # MB/s
                #print(f"{average_speed:.2f} MB/s")
                #progress_counter.set_postfix_str(f"{average_speed:.2f} MB/s")


                if TQDM_SHOW_PROGRESS:
                    self.downloaded_size += len(response.content)                                               # Update the downloaded size
                    self.class_ts_files_size.add_ts_file_size(len(response.content) * len(self.segments))       # Update the TS file size class
                    downloaded_size_str = format_size(self.downloaded_size)                                     # Format the downloaded size
                    estimate_total_size = self.class_ts_files_size.calculate_total_size()                       # Calculate the estimated total size
                    progress_counter.set_postfix_str(f"{Colors.WHITE}[ {Colors.GREEN}{downloaded_size_str.split(' ')[0]} {Colors.WHITE}< {Colors.GREEN}{estimate_total_size.split(' ')[0]} {Colors.RED}MB {Colors.WHITE}| {Colors.CYAN}{average_speed:.2f} {Colors.RED}MB/s")

                # Decrypt the segment content if decryption is needed
                if self.decryption is not None:
                    segment_content = self.decryption.decrypt(segment_content)

                with self.condition:
                    
                    self.segment_queue.put((index, segment_content))    # Add the segment to the queue
                    self.condition.notify()                             # Notify the writer thread that a new segment is available

                progress_counter.update(1)  # Update the progress counter

            else:
                logging.warning(f"Failed to download segment: {ts_url}")

        except Exception as e:
            logging.error(f"Exception while downloading segment: {e}")

    def write_segments_to_file(self, stop_event: threading.Event):
        """
        Writes downloaded segments to a file in the correct order.

        Args:
            - stop_event (threading.Event): Event to signal the stop of writing.
        """
         
        with open(self.tmp_file_path, 'ab') as f:
            while not stop_event.is_set() or not self.segment_queue.empty():
                with self.condition:
                    while self.segment_queue.empty() and not stop_event.is_set():
                        self.condition.wait()   # Wait until a new segment is available or stop_event is set

                    if not self.segment_queue.empty():

                        # Get the segment from the queue
                        index, segment_content = self.segment_queue.get()

                        # Write the segment to the file
                        if index == self.current_index:
                            f.write(segment_content)
                            self.current_index += 1
                            self.segment_queue.task_done()

                        else:
                            self.segment_queue.put((index, segment_content))    # Requeue the segment if it is not the next to be written
                            self.condition.notify()                             # Notify that a segment has been requeued                        # Notify that a segment has been requeued

    def download_streams(self, add_desc):
        """
        Downloads all TS segments in parallel and writes them to a file.

        Args:
            - add_desc (str): Additional description for the progress bar.
        """
        stop_event = threading.Event()  # Event to signal stopping

        # bar_format="{desc}: {percentage:.0f}% | {bar} | {n_fmt}/{total_fmt} [ {elapsed}<{remaining}, {rate_fmt}{postfix} ]"
        progress_bar = tqdm(
            total=len(self.segments), 
            unit='s',
            ascii=' #',
            bar_format=f"{Colors.YELLOW}Downloading {Colors.WHITE}({add_desc}{Colors.WHITE}): {Colors.RED}{{percentage:.0f}}% {Colors.MAGENTA}{{bar}} {Colors.YELLOW}{{elapsed}} {Colors.WHITE}< {Colors.CYAN}{{remaining}}{{postfix}} {Colors.WHITE}]",
            dynamic_ncols=True
        )

        def signal_handler(sig, frame):
            self.ctrl_c_detected = True  # Set global variable to indicate Ctrl+C detection

            stop_event.set()
            with self.condition:
                self.condition.notify_all()     # Wake up the writer thread if it's waiting

        # Register the signal handler for Ctrl+C
        signal.signal(signal.SIGINT, signal_handler)

        with ThreadPoolExecutor(max_workers=TQDM_MAX_WORKER) as executor:

            # Start a separate thread to write segments to the file
            writer_thread = threading.Thread(target=self.write_segments_to_file, args=(stop_event,))
            writer_thread.start()

            # Start progress monitor thread
            progress_thread = threading.Thread(target=self.timer, args=(progress_bar, stop_event))
            progress_thread.start()

            # Delay the start of each worker
            for index, segment_url in enumerate(self.segments):
                time.sleep(DELAY_START_WORKER)

                # da 0.0 a 100.00
                if int(LIMIT_DONWLOAD_PERCENTAGE) != 0:
                    score_percentage = (progress_bar.n / progress_bar.total) * 100
                    if score_percentage>= LIMIT_DONWLOAD_PERCENTAGE:
                        #progress_bar.refresh()
                        break


                # Check for Ctrl+C before starting each download task
                time.sleep(0.025)

                if self.ctrl_c_detected:
                    console.log("[red]1. Ctrl+C detected. Stopping further downloads.")

                    stop_event.set()
                    with self.condition:
                        self.condition.notify_all()     # Wake up the writer thread if it's waiting

                    break

                # Submit the download task to the executor
                executor.submit(self.make_requests_stream, segment_url, index, stop_event, progress_bar, add_desc)

            # Wait for all segments to be downloaded
            executor.shutdown(wait=True)
            stop_event.set()                    # Set the stop event to halt the writer thread
            with self.condition:
                self.condition.notify_all()     # Wake up the writer thread if it's waiting
            writer_thread.join()                # Wait for the writer thread to finish

    def timer(self, progress_counter: tqdm, quit_event: threading.Event):
            """
            Function to monitor progress and quit if no progress is made within a certain time
            
            Args:
                - progress_counter (tqdm): The progress counter object.
                - quit_event (threading.Event): The event to signal when to quit.
            """

            # If timer is disabled, return immediately without starting it, to reduce cpu use
            if not ENABLE_TIME_TIMEOUT:
                return

            start_time = time.time()
            last_count = 0

            # Loop until quit event is set
            while not quit_event.is_set():
                current_count = progress_counter.n

                # Update start time when progress is made
                if current_count != last_count:
                    start_time = time.time() 
                    last_count = current_count

                # Calculate elapsed time
                elapsed_time = time.time() - start_time

                # Check if elapsed time exceeds progress timeout
                if elapsed_time > TQDM_PROGRESS_TIMEOUT:
                    console.log(f"[red]No progress for {TQDM_PROGRESS_TIMEOUT} seconds. Stopping.")

                    # Set quit event to break the loop
                    quit_event.set()
                    break
                
                # Calculate remaining time until timeout
                remaining_time = max(0, TQDM_PROGRESS_TIMEOUT - elapsed_time)

                # Determine sleep interval dynamically based on remaining time
                sleep_interval = min(1, remaining_time)

                # Wait for the calculated sleep interval
                time.sleep(sleep_interval)

            # Refresh progress bar
            #progress_counter.refresh()
