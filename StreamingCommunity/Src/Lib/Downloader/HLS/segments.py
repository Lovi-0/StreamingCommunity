# 18.04.24

import os
import sys
import time
import queue
import logging
import binascii
import threading
import signal
from queue import PriorityQueue
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed


# External libraries
import httpx
from tqdm import tqdm


# Internal utilities
from StreamingCommunity.Src.Util.console import console
from StreamingCommunity.Src.Util.headers import get_headers, random_headers
from StreamingCommunity.Src.Util.color import Colors
from StreamingCommunity.Src.Util._jsonConfig import config_manager
from StreamingCommunity.Src.Util.os import os_manager
from StreamingCommunity.Src.Util.call_stack import get_call_stack


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
REQUEST_MAX_RETRY = config_manager.get_int('REQUESTS', 'max_retry')
REQUEST_VERIFY = config_manager.get_bool('REQUESTS', 'verify_ssl')
THERE_IS_PROXY_LIST = os_manager.check_file("list_proxy.txt")
PROXY_START_MIN = config_manager.get_float('REQUESTS', 'proxy_start_min')
PROXY_START_MAX = config_manager.get_float('REQUESTS', 'proxy_start_max')
DEFAULT_VIDEO_WORKERS = config_manager.get_int('M3U8_DOWNLOAD', 'default_video_workser')
DEFAULT_AUDIO_WORKERS = config_manager.get_int('M3U8_DOWNLOAD', 'default_audio_workser')


# Variable
headers_index = config_manager.get_dict('REQUESTS', 'user-agent')
max_timeout = config_manager.get_int("REQUESTS", "timeout")



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
        self.downloaded_segments = set()

        # Stopping
        self.interrupt_flag = threading.Event()
        self.download_interrupted = False

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
            response = httpx.get(
                url=key_uri, 
                headers=headers_index,
                timeout=max_timeout
            )
            response.raise_for_status()

        except Exception as e:
            raise Exception(f"Failed to fetch key from {key_uri}: {e}")

        # Convert the content of the response to hexadecimal and then to bytes
        hex_content = binascii.hexlify(response.content).decode('utf-8')
        byte_content = bytes.fromhex(hex_content)
        
        return byte_content
    
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

    def get_info(self) -> None:
        """
        Makes a request to the index M3U8 file to get information about segments.
        """
        headers_index = {'user-agent': get_headers()}

        if self.is_index_url:

            # Send a GET request to retrieve the index M3U8 file
            response = httpx.get(
                self.url, 
                headers=headers_index, 
                timeout=max_timeout
            )
            response.raise_for_status()

            # Save the M3U8 file to the temporary folder
            path_m3u8_file = os.path.join(self.tmp_folder, "playlist.m3u8")
            open(path_m3u8_file, "w+").write(response.text) 

            # Parse the text from the M3U8 index file
            self.parse_data(response.text)  

        else:

            # Parser data of content of index pass in input to class
            self.parse_data(self.url)
    
    def setup_interrupt_handler(self):
        """
        Set up a signal handler for graceful interruption.
        """
        def interrupt_handler(signum, frame):
            if not self.interrupt_flag.is_set():
                console.log("\n[red] Stopping download gracefully...")
                self.interrupt_flag.set()
                self.download_interrupted = True
                self.stop_event.set()

        signal.signal(signal.SIGINT, interrupt_handler)

    def make_requests_stream(self, ts_url: str, index: int, progress_bar: tqdm, retries: int = 3, backoff_factor: float = 1.5) -> None:
        """
        Downloads a TS segment and adds it to the segment queue with retry logic.

        Parameters:
            - ts_url (str): The URL of the TS segment.
            - index (int): The index of the segment.
            - progress_bar (tqdm): Progress counter for tracking download progress.
            - retries (int): The number of times to retry on failure (default is 3).
            - backoff_factor (float): The backoff factor for exponential backoff (default is 1.5 seconds).
        """
        if self.interrupt_flag.is_set():
            return
        
        need_verify = REQUEST_VERIFY
        min_segment_size = 100  # Minimum acceptable size for a TS segment in bytes

        for attempt in range(retries):
            if self.interrupt_flag.is_set():
                return
            
            try:
                start_time = time.time()
                
                # Make request to get content
                if THERE_IS_PROXY_LIST:

                    # Get proxy from list
                    proxy = self.valid_proxy[index % len(self.valid_proxy)]
                    logging.info(f"Use proxy: {proxy}")

                    with httpx.Client(proxies=proxy, verify=need_verify) as client:  
                        if 'key_base_url' in self.__dict__:
                             response = client.get(
                                url=ts_url, 
                                headers=random_headers(self.key_base_url), 
                                timeout=max_timeout, 
                                follow_redirects=True
                            )
                             
                        else:
                            response = client.get(
                                url=ts_url, 
                                headers={'user-agent': get_headers()}, 
                                timeout=max_timeout, 
                                follow_redirects=True
                            )

                else:
                    with httpx.Client(verify=need_verify) as client_2:
                        if 'key_base_url' in self.__dict__:
                            response = client_2.get(
                                url=ts_url, 
                                headers=random_headers(self.key_base_url), 
                                timeout=max_timeout, 
                                follow_redirects=True
                            )

                        else:
                            response = client_2.get(
                                url=ts_url, 
                                headers={'user-agent': get_headers()}, 
                                timeout=max_timeout, 
                                follow_redirects=True
                            )

                # Validate response and content
                response.raise_for_status()
                segment_content = response.content
                content_size = len(segment_content)

                # Check if segment is too small (possibly corrupted or empty)
                if content_size < min_segment_size:
                    raise httpx.RequestError(f"Segment {index} too small ({content_size} bytes)")

                duration = time.time() - start_time

                # Decrypt if needed and verify decrypted content
                if self.decryption is not None:
                    try:
                        segment_content = self.decryption.decrypt(segment_content)
                        if len(segment_content) < min_segment_size:
                            raise Exception(f"Decrypted segment {index} too small ({len(segment_content)} bytes)")
                        
                    except Exception as e:
                        logging.error(f"Decryption failed for segment {index}: {str(e)}")
                        raise

                # Update progress and queue
                self.class_ts_estimator.update_progress_bar(content_size, duration, progress_bar)

                # Add the segment to the queue
                self.queue.put((index, segment_content))

                # Track successfully downloaded segments
                self.downloaded_segments.add(index)  
                progress_bar.update(1)

                # Break out of the loop on success
                return

            except Exception as e:
                #logging.error(f"Attempt {attempt + 1} failed for segment {index} - '{ts_url}': {e}")
                
                if attempt + 1 == retries:
                    #logging.error(f"Final retry failed for segment {index}")
                    self.queue.put((index, None))  # Marker for failed segment
                    progress_bar.update(1)
                    break
                
                sleep_time = backoff_factor * (2 ** attempt)
                logging.info(f"Retrying segment {index} in {sleep_time} seconds...")
                time.sleep(sleep_time)

    def write_segments_to_file(self):
        """
        Writes segments to file with additional verification.
        """
        with open(self.tmp_file_path, 'wb') as f:
            expected_index = 0
            buffer = {}
            total_written = 0
            segments_written = set()

            while not self.stop_event.is_set() or not self.queue.empty():
                
                if self.interrupt_flag.is_set():
                    break
                
                try:
                    index, segment_content = self.queue.get(timeout=1)

                    # Handle failed segments
                    if segment_content is None:
                        if index == expected_index:
                            expected_index += 1
                        continue

                    # Write segment if it's the next expected one
                    if index == expected_index:
                        f.write(segment_content)
                        total_written += len(segment_content)
                        segments_written.add(index)
                        f.flush()
                        expected_index += 1

                        # Write any buffered segments that are now in order
                        while expected_index in buffer:
                            next_segment = buffer.pop(expected_index)
                            if next_segment is not None:
                                f.write(next_segment)
                                total_written += len(next_segment)
                                segments_written.add(expected_index)
                                f.flush()
                            expected_index += 1
                    else:
                        buffer[index] = segment_content

                except queue.Empty:
                    if self.stop_event.is_set():
                        break
                    continue
                except Exception as e:
                    logging.error(f"Error writing segment {index}: {str(e)}")
                    continue

            # Final verification
            if total_written == 0:
                raise Exception("No data written to file")
    
    def download_streams(self, add_desc):
        """
        Downloads all TS segments in parallel and writes them to a file.

        Parameters:
            - add_desc (str): Additional description for the progress bar.
        """
        self.setup_interrupt_handler()

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
        except:
            #VIDEO_WORKERS = os.cpu_count()
            VIDEO_WORKERS = DEFAULT_VIDEO_WORKERS

        try:
            AUDIO_WORKERS = int(config_manager.get_dict('SITE', config_site)['audio_workers'])
        except:
            #AUDIO_WORKERS = os.cpu_count()
            AUDIO_WORKERS = DEFAULT_AUDIO_WORKERS

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

        try:

            # Start writer thread
            writer_thread = threading.Thread(target=self.write_segments_to_file)
            writer_thread.daemon = True
            writer_thread.start()

            # Configure workers and delay
            max_workers = len(self.valid_proxy) if THERE_IS_PROXY_LIST else TQDM_MAX_WORKER
            delay = max(PROXY_START_MIN, min(PROXY_START_MAX, 1 / (len(self.valid_proxy) + 1))) if THERE_IS_PROXY_LIST else TQDM_DELAY_WORKER

            # Download segments with completion verification
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for index, segment_url in enumerate(self.segments):
                    # Check for interrupt before submitting each task
                    if self.interrupt_flag.is_set():
                        break

                    time.sleep(delay)
                    futures.append(executor.submit(self.make_requests_stream, segment_url, index, progress_bar))

                # Wait for futures with interrupt handling
                for future in as_completed(futures):
                    if self.interrupt_flag.is_set():
                        break
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f"Error in download thread: {str(e)}")

                # Interrupt handling for missing segments
                if not self.interrupt_flag.is_set():
                    total_segments = len(self.segments)
                    completed_segments = len(self.downloaded_segments)
                    
                    if completed_segments < total_segments:
                        missing_segments = set(range(total_segments)) - self.downloaded_segments
                        logging.warning(f"Missing segments: {sorted(missing_segments)}")
                        
                        # Retry missing segments with interrupt check
                        for index in missing_segments:
                            if self.interrupt_flag.is_set():
                                break
                            try:
                                self.make_requests_stream(self.segments[index], index, progress_bar)
                            except Exception as e:
                                logging.error(f"Failed to retry segment {index}: {str(e)}")

        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            raise

        finally:

            # Clean up resources
            self.stop_event.set()
            writer_thread.join(timeout=30)
            progress_bar.close()

            # Check if download was interrupted
            if self.download_interrupted:
                console.log("[red] Download was manually stopped.")

                # Optional: Delete partial download
                if os.path.exists(self.tmp_file_path):
                    os.remove(self.tmp_file_path)
                sys.exit(0)

        # Clean up
        self.stop_event.set()
        writer_thread.join(timeout=30)
        progress_bar.close()

        # Final verification
        final_completion = (len(self.downloaded_segments) / total_segments) * 100
        if final_completion < 99.9:  # Less than 99.9% complete
            missing = set(range(total_segments)) - self.downloaded_segments
            raise Exception(f"Download incomplete ({final_completion:.1f}%). Missing segments: {sorted(missing)}")

        # Verify output file
        if not os.path.exists(self.tmp_file_path):
            raise Exception("Output file missing")
        
        file_size = os.path.getsize(self.tmp_file_path)
        if file_size == 0:
            raise Exception("Output file is empty")
        
        logging.info(f"Download completed. File size: {file_size} bytes")
