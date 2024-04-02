# 5.01.24 -> 7.01.24 -> 20.02.24 -> 29.03.24

# Importing modules
import os
import sys
import time
import threading
import logging
import warnings

# Disable specific warnings
from tqdm import TqdmExperimentalWarning
warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="cryptography")

# External libraries
import requests
from tqdm.rich import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Internal utilities
from Src.Util.console import console
from Src.Util.headers import get_headers
from Src.Util.config import config_manager
from Src.Util.os import (
    remove_folder, 
    remove_file, 
    format_size, 
    compute_sha1_hash,
    convert_to_hex
)

# Logic class
from .util import (
    print_duration_table,
    concatenate_and_save,
    join_audios,
    transcode_with_subtitles
)
from .util import (
    M3U8_Decryption,
    M3U8_Ts_Files,
    M3U8_Parser,
    M3U8_UrlFix
)

# Config
Download_audio = config_manager.get_bool('M3U8_OPTIONS', 'download_audio')
Donwload_subtitles = config_manager.get_bool('M3U8_OPTIONS', 'download_subtitles')
DOWNLOAD_SPECIFIC_AUDIO = config_manager.get_list('M3U8_OPTIONS', 'specific_list_audio')            
DOWNLOAD_SPECIFIC_SUBTITLE = config_manager.get_list('M3U8_OPTIONS', 'specific_list_subtitles')
TQDM_MAX_WORKER = config_manager.get_int('M3U8', 'tdqm_workers')
TQDM_PROGRESS_TIMEOUT = config_manager.get_int('M3U8', 'tqdm_progress_timeout')
COMPLETED_PERCENTAGE = config_manager.get_float('M3U8', 'download_percentage')
REQUESTS_TIMEOUT = config_manager.get_int('M3U8', 'requests_timeout')
ENABLE_TIME_TIMEOUT = config_manager.get_bool('M3U8', 'enable_time_quit')
TQDM_SHOW_PROGRESS = config_manager.get_bool('M3U8', 'tqdm_show_progress')
MIN_TS_FILES_IN_FOLDER = config_manager.get_int('M3U8', 'minimum_ts_files_in_folder')
REMOVE_SEGMENTS_FOLDER = config_manager.get_bool('M3U8', 'cleanup_tmp_folder')

# Variable
config_headers = config_manager.get_dict('M3U8_OPTIONS', 'request')
failed_segments = []
class_urlFix = M3U8_UrlFix()

# [ main class ]

class M3U8_Segments:
    def __init__(self, url, folder, key=None):
        """
        Initializes M3U8_Segments with the provided URL and optional decryption key.

        Args:
        - url (str): The URL of the M3U8 file.
        - key (str, optional): The decryption key. Defaults to None.
        """

        self.url = url
        self.key = key

        # Init M3U8_Decryption class if key is present
        if self.key is not None: 
            self.decryption = M3U8_Decryption(key)

        # Generate temp base folder based on hash of url
        self.downloaded_size = 0
        self.temp_folder = folder
        os.makedirs(self.temp_folder, exist_ok=True)

        # Config
        self.enable_timer = ENABLE_TIME_TIMEOUT
        self.progress_timeout = TQDM_PROGRESS_TIMEOUT
        self.class_ts_files_size = M3U8_Ts_Files()

    def parse_data(self, m3u8_content: str) -> None:
        """
        Parses the M3U8 content to extract segment information.

        Args:
            m3u8_content (str): The content of the M3U8 file.
        """

        try:
            # Parse index m3u8 content from request(m3u8).text
            m3u8_parser = M3U8_Parser(DOWNLOAD_SPECIFIC_SUBTITLE)
            m3u8_parser.parse_data(m3u8_content)

            # Add decryption iv if key has the same byte string
            if self.key is not None and m3u8_parser.keys.get('iv') is not None:

                iv = m3u8_parser.keys.get('iv')
                method = m3u8_parser.keys.get('method')
                
                # Add iv for decryption to M3U8_Decryption
                logging.info(f"[M3U8_Segments] Parameter iv => {iv}")
                self.decryption.parse_key(iv)

                # Add method for decryption to M3U8_Decryption
                logging.info(f"[M3U8_Segments] Set method => {method}")
                self.decryption.set_method(method)

            # Store segments
            self.segments = m3u8_parser.segments
            logging.info("[M3U8_Segments] Segments extracted successfully.")
            
        except Exception as e:
            logging.error(f"[M3U8_Segments] Error parsing M3U8 content: {e}")

    def get_info(self) -> None:
        """
        Makes a request to the index m3u8 file to get information about segments.
        """

        try:
            # Add random user agent to config headers
            config_headers['index']['user-agent'] = get_headers()

            # Send a GET request to retrieve the index m3u8 file
            response = requests.get(self.url, headers=config_headers['index'])
            response.raise_for_status()  # Raise HTTPError for non-2xx status codes

            # Parse text from request to m3u8 index
            self.parse_data(response.text)
            logging.info(f"[M3U8_Segments] Ts segments found: {len(self.segments)}")

        except requests.exceptions.RequestException as req_err:
            logging.error(f"[M3U8_Segments] Error occurred during request: {req_err}")
            sys.exit(1)  # Exit with non-zero status to indicate an error

        except Exception as e:
            logging.error(f"[M3U8_Segments] Error occurred: {e}")

    def is_valid_ts_url(self, ts_url: str) -> bool:
        """
        Check if the given ts URL is valid.

        Args:
            ts_url (str): The URL of the ts file.
            failed_segments (list): List of failed segment URLs.

        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        # Check if the URL exists in the list of segments and is not in the list of failed segments
        for failed_seg in failed_segments:
            if str(failed_seg) in ts_url:
                return False
            
        return True

    def make_reqests_stream(self, ts_url: str) -> bytes:
        """
        Make a single request to a ts file to get content.

        Args:
            ts_url (str): The URL of the ts file.

        Returns:
            bytes or None: The content of the requested ts file if successful, otherwise None.
        """

        try:

            # Fix URL if it is incomplete (missing 'http')
            if "http" not in ts_url:
                ts_url = class_urlFix.generate_full_url(ts_url)
                logging.info(f"Generated new URL: {ts_url}")

            # Check if the ts_url is valid
            is_valid_url = self.is_valid_ts_url(ts_url)

            if is_valid_url:
                # Generate random user agent for segments request
                headers = config_headers.get('segments')
                headers['user-agent'] = get_headers()

                # Make GET request to ts audio or video file with a random user agent
                response = requests.get(ts_url, headers=headers, timeout=REQUESTS_TIMEOUT)

                # If the response status code is not 200, mark the URL as failed
                if response.status_code != 200:
                    logging.error(f"Failed to fetch content from {ts_url}. Status code: {response.status_code}")
                    return None

                # Return the content if the request is successful
                return response.content

            else:
                logging.info(f"Skipping invalid URL: {ts_url}")
                return None

        except requests.exceptions.RequestException as req_err:
            logging.error(f"Error occurred during request to {ts_url}: {req_err}")
            return None

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return None

    def save_stream(self, index: int, progress_counter: tqdm, stop_event: threading.Event) -> None:
        """
        Save ts file and decrypt if there is an iv present in the decryption class.

        Parameters:
        - index (int): The index of the ts file in the segments list.
        - progress_counter (tqdm): The progress counter object.
        - stop_event (threading.Event): The event to signal when to quit.
        """
        # Break if stop event is true
        if stop_event.is_set():
            return

        try:
            # Get ts url and create a filename based on index
            ts_url = self.segments[index]
            ts_filename = os.path.join(self.temp_folder, f"{index}.ts")
            logging.info(f"Requesting: {ts_url}, saving to: {ts_filename}")

            # If file already exists, skip download
            if os.path.exists(ts_filename):
                logging.info(f"Skipping download. File already exists: {ts_filename}")
                return

            # Get bytes of ts data
            ts_content = self.make_reqests_stream(ts_url)

            # If data is retrieved
            if ts_content is not None:
                # Create a file to save data
                with open(ts_filename, "wb") as ts_file:
                    # Decrypt if there is an IV in the main M3U8 index
                    if self.key and self.decryption.iv:
                        decrypted_data = self.decryption.decrypt(ts_content)
                        ts_file.write(decrypted_data)
                    else:
                        ts_file.write(ts_content)

                # Update downloaded size
                if TQDM_SHOW_PROGRESS:
                    self.downloaded_size += len(ts_content)
                    self.class_ts_files_size.add_ts_file_size(len(ts_content) * len(self.segments))

        except Exception as e:
            logging.error(f"Error saving TS file: {e}")

        finally:
            # Update progress counter
            progress_counter.update(1)

            if TQDM_SHOW_PROGRESS:
                downloaded_size_str = format_size(self.downloaded_size)
                estimate_total_size = self.class_ts_files_size.calculate_total_size()
                progress_counter.set_description(f"[yellow]Download [red][{index}] - [{downloaded_size_str} / {estimate_total_size}]")
            else:
                progress_counter.set_description(f"[yellow]Download")

            # Refresh progress bar
            progress_counter.refresh()

    def donwload_streams(self):
        """
        Downloads TS segments in parallel using ThreadPoolExecutor.

        """
        try:
            # Initialize progress bar
            progress_counter = tqdm(total=len(self.segments), unit=" segment", desc="[yellow]Download")

            # Event to signal stop condition for progress monitoring
            stop_event = threading.Event()

            # Start progress monitor thread
            progress_thread = threading.Thread(target=self.timer, args=(progress_counter, stop_event))
            progress_thread.start()

            # Create ThreadPoolExecutor for parallel downloading
            with ThreadPoolExecutor(max_workers=TQDM_MAX_WORKER) as executor:
                futures = []

                # Submit tasks for downloading segments
                for index in range(len(self.segments)):
                    future = executor.submit(self.save_stream, index, progress_counter, stop_event)
                    futures.append(future)

                try:
                    # Wait for tasks to complete
                    for future in as_completed(futures):
                        future.result()

                        # Check if progress reached 99%
                        if progress_counter.n >= len(self.segments) * COMPLETED_PERCENTAGE:
                            #console.log(f"[yellow]Progress reached {COMPLETED_PERCENTAGE*100}%. Stopping.")
                            progress_counter.refresh()
                            break

                except KeyboardInterrupt:
                    console.log("[red]Ctrl+C detected. Exiting gracefully [white]...")
                    stop_event.set()

        except KeyboardInterrupt:
            logging.info("Ctrl+C detected. Exiting gracefully...")

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

        finally:
            # Signal stop event to end progress monitor thread
            stop_event.set()

            # Wait for progress monitor thread to finish
            progress_thread.join()

    def timer(self, progress_counter: tqdm, quit_event: threading.Event):
        """
        Function to monitor progress and quit if no progress is made within a certain time
        
        Parameters:
        - progress_counter (tqdm): The progress counter object.
        - quit_event (threading.Event): The event to signal when to quit.
        """

        # If timer is disabled, return immediately without starting it, to reduce cpu use
        if not self.enable_timer:
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
            if elapsed_time > self.progress_timeout:
                console.log(f"[red]No progress for {self.progress_timeout} seconds. Stopping.")

                # Set quit event to break the loop
                quit_event.set()
                break
            
            # Calculate remaining time until timeout
            remaining_time = max(0, self.progress_timeout - elapsed_time)

            # Determine sleep interval dynamically based on remaining time
            sleep_interval = min(1, remaining_time)

            # Wait for the calculated sleep interval
            time.sleep(sleep_interval)

        # Refresh progress bar
        progress_counter.refresh()

    def join(self, output_filename: str, video_decoding: str = None, audio_decoding: str = None):
        """
        Join all segments file to a mp4 file name
        !! NOT USED
        
        Parameters:
        - video_decoding(str): video decoding to use with ffmpeg for only video
        - audio_decoding(str): audio decoding to use with ffmpeg for only audio
        - output_filename (str): The name of the output mp4 file.
        """

        # Print output of failed segments if present
        if len(failed_segments) > 0:
            logging.error(f"[M3U8_Segments] Failed segments = {failed_segments}")
            logging.warning("[M3U8_Segments] Audio and video can be out of sync !!!")
            console.log("[red]Audio and video can be out of sync !!!")
        
        # Get current dir and create file_list with path of all ts file
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_list_path = os.path.join(current_dir, 'file_list.txt')

        # Sort files (1.ts, 2.ts, ...)
        ts_files = [f for f in os.listdir(self.temp_folder) if f.endswith(".ts")]
        def extract_number(file_name):
            return int(''.join(filter(str.isdigit, file_name)))
        ts_files.sort(key=extract_number)

        # Check if there is file to json
        if len(ts_files) < MIN_TS_FILES_IN_FOLDER:
            logging.error(f"No .ts file to join in folder: {self.temp_folder}")
            sys.exit(0)

        # Save files sorted in a txt file with absolute path to fix problem with ( C:\\path (win))
        with open(file_list_path, 'w') as file_list:
            for ts_file in ts_files:
                absolute_path = os.path.abspath(os.path.join(self.temp_folder, ts_file))
                file_list.write(f"file '{absolute_path}'\n")

        console.log("[cyan]Start joining all files")

        # ADD IF 
        concatenate_and_save(
            file_list_path = file_list_path,
            output_filename = output_filename,
            video_decoding = video_decoding,
            audio_decoding = audio_decoding 
        )


class Downloader():
    def __init__(self, output_filename: str = None, m3u8_playlist:str = None,  m3u8_index:str = None, key: str = None):

        """
        Initialize the Downloader object.

        Parameters:
        - output_filename (str): Output filename for the downloaded content.
        - m3u8_playlist (str, optional): URL to the main M3U8 playlist.
        - key (str, optional): Hexadecimal representation of the encryption key.
        """


        self.m3u8_playlist = m3u8_playlist
        self.m3u8_index = m3u8_index
        self.key = bytes.fromhex(key) if key is not None else key
        self.output_filename = output_filename

        # Auto generate out file name if not present
        if output_filename == None:
            if m3u8_playlist != None:
                self.output_filename = os.path.join("missing", compute_sha1_hash(m3u8_playlist))
            else:
                self.output_filename = os.path.join("missing", compute_sha1_hash(m3u8_index))

        if self.key != None:
            hex_data = convert_to_hex(self.key)
            console.log(f"[cyan]Key use [white]=> [red]{hex_data}")

        # Initialize temp base path
        self.base_path = os.path.join(str(self.output_filename).replace(".mp4", ""))
        self.video_segments_path = os.path.join(self.base_path, "tmp", "video")
        self.audio_segments_path = os.path.join(self.base_path, "tmp", "audio")
        self.subtitle_segments_path = os.path.join(self.base_path, "tmp", "subtitle")

        # Create temp folder
        logging.info("Create temp folder")
        os.makedirs(self.video_segments_path, exist_ok=True)
        os.makedirs(self.audio_segments_path, exist_ok=True)
        os.makedirs(self.subtitle_segments_path, exist_ok=True)

        # Track subtitle, audio donwload
        self.downloaded_audio = []
        self.downloaded_subtitle = []
        self.downloaded_video = []

        # Default decoding
        self.video_decoding = "avc1.640028"
        self.audio_decoding = "mp4a.40.2"
 
    def __df_make_req__(self, url: str) -> str:
        """
        Make a request to get text from the provided URL.

        Parameters:
        - url (str): The URL to make the request to.

        Returns:
        - str: The text content of the response.
        """
        try:
            # Send a GET request to the provided URL
            config_headers.get('index')['user-agent'] = get_headers()
            response = requests.get(url, headers=config_headers.get('index'))

            if response.ok:
                return response.text
            else:
                logging.error(f"[df_make_req] Request to {url} failed with status code: {response.status_code}")
                return None

        except requests.RequestException as req_err:
            logging.error(f"[df_make_req] Error occurred during request: {req_err}")
            return None

        except Exception as e:
            logging.error(f"[df_make_req] An unexpected error occurred: {e}")
            return None
        
    def manage_playlist(self, m3u8_playlist_text):
        """
        Parses the M3U8 playlist to extract information about keys, playlists, subtitles, etc.

        Args:
            m3u8_playlist_text (str): The text content of the M3U8 playlist.
        """

        global Download_audio, Donwload_subtitles

        # Create an instance of the M3U8_Parser class
        parse_class_m3u8 = M3U8_Parser(DOWNLOAD_SPECIFIC_SUBTITLE)

        # Extract information about the M3U8 playlist
        parse_class_m3u8.parse_data(m3u8_playlist_text)

        # Collect available audio tracks and default audio track
        self.list_available_audio = parse_class_m3u8.get_track_audios()
        self.default_audio = parse_class_m3u8.get_default_track_audio()

        # Check if there is some audios, else disable download
        if self.list_available_audio != None:
            console.log(f"[cyan]Find audios language: [red]{[obj_audio.get('language') for obj_audio in self.list_available_audio]}")
        else:
            console.log("[red]Cant find a list of audios")
            Download_audio = False

        # Collect available subtitles and default subtitle
        self.list_available_subtitles = parse_class_m3u8.get_subtitles()
        self.default_subtitle = parse_class_m3u8.get_default_subtitle()

        # Check if there is some subtitles, else disable download
        if self.list_available_subtitles != None:
            console.log(f"[cyan]Find subtitles language: [red]{[obj_sub.get('language') for obj_sub in self.list_available_subtitles]}")
        else:
            console.log("[red]Cant find a list of audios")
            Donwload_subtitles = False

        # Collect best quality video
        m3u8_index_obj = parse_class_m3u8.get_best_quality()

        # Get URI of the best quality and codecs parameters
        console.log(f"[cyan]Select resolution: [red]{m3u8_index_obj.get('width')}")
        m3u8_index = m3u8_index_obj.get('uri')
        m3u8_index_decoding = m3u8_index_obj.get('codecs')

        # Fix URL if it is not complete with http:\\site_name.domain\...
        if "http" not in m3u8_index:

            # Generate full URL
            m3u8_index = class_urlFix.generate_full_url(m3u8_index)

            # Check if a valid HTTPS URL is obtained
            if m3u8_index is not None and "https" in m3u8_index:
                console.log(f"[cyan]Found m3u8 index [white]=> [red]{m3u8_index}")
            else:
                logging.warning("[download_m3u8] Can't find a valid m3u8 index")
                sys.exit(0)

        # Collect best index, video decoding, and audio decoding
        self.m3u8_index = m3u8_index

        # if is present in playlist
        if m3u8_index_decoding != None:
            self.video_decoding = m3u8_index_decoding.split(",")[0] 
            self.audio_decoding = m3u8_index_decoding.split(",")[1]

    def manage_subtitle(self):
        """
        Downloads and manages subtitles.

        This method iterates over available subtitles, downloads them if necessary, and updates
        the list of downloaded subtitles.
        """

        # Iterate over each available subtitle
        for obj_subtitle in self.list_available_subtitles:
            logging.info(f"(manage_subtitle) Find => {obj_subtitle}")

            # Check if there is custom subtitles to download
            if len(DOWNLOAD_SPECIFIC_SUBTITLE) > 0:
                
                # Check if language in list
                if obj_subtitle.get('language') not in DOWNLOAD_SPECIFIC_SUBTITLE:
                    continue

            # Construct full path for the subtitle file
            sub_full_path = os.path.join(self.subtitle_segments_path, obj_subtitle.get('language') + ".vtt")

            # Check if the subtitle file already exists
            if not os.path.exists(sub_full_path):
                console.log(f"[cyan]Download subtitle [white]=> [red]{obj_subtitle.get('language')}.")

            # Add the subtitle to the list of downloaded subtitles
            self.downloaded_subtitle.append({
                'name': obj_subtitle.get('name').split(" ")[0],
                'language': obj_subtitle.get('language').upper(),
                'path': os.path.abspath(sub_full_path)
            })


            # If the subtitle file doesn't exist, download it
            response = requests.get(obj_subtitle.get('uri'))
            open(sub_full_path, "wb").write(response.content)

    def manage_audio(self):
        """
        Downloads and manages audio segments.

        This method iterates over available audio tracks, downloads them if necessary, and updates
        the list of downloaded audio tracks.
        """

        # Iterate over each available audio track
        for obj_audio in self.list_available_audio:
            logging.info(f"(manage_audio) Find => {obj_audio}")

            # Check if there is custom subtitles to download
            if len(DOWNLOAD_SPECIFIC_AUDIO) > 0:

                # Check if language in list
                if obj_audio.get('language') not in DOWNLOAD_SPECIFIC_AUDIO:
                    continue

            # Construct full path for the audio segment directory
            full_path_audio = os.path.join(self.audio_segments_path, obj_audio.get('language'))

            self.downloaded_audio.append({
                'language': obj_audio.get('language'),
                'path': full_path_audio
            })

            # Check if the audio segment directory already exists
            if not os.path.exists(full_path_audio):

                # If the audio segment directory doesn't exist, download audio segments
                audio_m3u8 = M3U8_Segments(obj_audio.get('uri'), full_path_audio, self.key)
                console.log(f"[purple]Download audio segments [white]=> [red]{obj_audio.get('language')}.")

                # Get information about the audio segments
                audio_m3u8.get_info()
                
                # Download the audio segments
                audio_m3u8.donwload_streams()

    def manage_video(self):
        """
        Downloads and manages video segments.

        This method downloads video segments if necessary and updates
        the list of downloaded video segments.
        """

        # Construct full path for the video segment directory
        full_path_video = self.video_segments_path
        
        # Create an instance of M3U8_Segments to handle video segments
        video_m3u8 = M3U8_Segments(self.m3u8_index, full_path_video, self.key)
        console.log("[purple]Download video segments.")
        
        # Add the video segment directory to the list of downloaded video segments
        self.downloaded_video.append({
            'path': full_path_video
        })

        # Get information about the video segments
        video_m3u8.get_info()
        
        # Download the video segments
        video_m3u8.donwload_streams()

    @staticmethod
    def extract_number(file_name):
        return int(''.join(filter(str.isdigit, file_name)))

    def join_ts_files(self, full_path: str, out_file_name: str):
        """
        Joins the individual .ts files into a single video file.

        Args:
            full_path (str): The full path to the directory containing the .ts files.
            out_file_name (str): The name of the output video file.

        Returns:
            str: The path to the output video file.
        """

        # Get the current directory and create a file_list with the path of all .ts files
        file_list_path = os.path.join('file_list.txt')

        # Sort files (1.ts, 2.ts, ...) based on their numbers
        ts_files = [f for f in os.listdir(full_path) if f.endswith(".ts")]
        ts_files.sort(key=Downloader.extract_number)

        # Check if there are enough .ts files to join (at least 10)
        if len(ts_files) < 10:
            logging.error(f"No .ts file to join in folder: {full_path}")

        else:

            # Save files sorted in a txt file with absolute path to fix problem with ( C:\\path (win))
            with open(file_list_path, 'w') as file_list:
                for ts_file in ts_files:
                    #absolute_path = os.path.abspath(os.path.join(full_path, ts_file))
                    relative_path = os.path.relpath(os.path.join(full_path, ts_file))
                    file_list.write(f"file '{relative_path}'\n")

            # Concatenate and save the files and return the path to the output filename
            return concatenate_and_save(
                file_list_path=file_list_path,
                output_filename=out_file_name,
                video_decoding=self.video_decoding,
                audio_decoding=self.audio_decoding
            )

    def download_audios(self):
        """
        Downloads audio files and stores their paths.
        """

        # Initialize an empty list to store audio tracks paths
        self.audio_tracks_path = []

        # Check if there are any downloaded audio objects
        if len(self.downloaded_audio) > 0:

            # Iterate over each downloaded audio object
            for obj_downloaded_audio in self.downloaded_audio:

                # Create the expected path for the audio file based on its language
                obj_audio_path = os.path.join(self.base_path, obj_downloaded_audio.get('language') + ".mp4")
                    
                # Check if the audio file already exists
                if not os.path.exists(obj_audio_path):

                    # If the audio file doesn't exist, join the .ts files and save as .mp4
                    new_audio_path = self.join_ts_files(
                        obj_downloaded_audio.get('path'),
                        obj_audio_path
                    )

                    console.log(f"[cyan]Join segments: [red]{obj_downloaded_audio.get('language')}")

                    # Add the joined audio file path to the list
                    self.audio_tracks_path.append({
                        'path': new_audio_path
                    })

    def download_videos(self):
        """
        Downloads video files and stores their path.
        """

        # Construct the expected path for the video file
        video_track_path = os.path.join(self.base_path, "video.mp4")
        console.log(f"[cyan]Join segments: [red]video")

        # Check if the video file already exists
        if not os.path.exists(video_track_path):

            # If the video file doesn't exist, join the .ts files and save as .mp4
            video_track_path = self.join_ts_files(
                self.downloaded_video[0].get('path'),
                video_track_path
            )

        # Get info video
        print_duration_table(video_track_path)

        self.video_track_path = video_track_path

    def add_subtitles_audios(self):
        """Add subtitles and audio tracks to the video.

        This function checks if there are any audio tracks and adds them to the video if available.
        It also adds subtitles to the video if there are any downloaded. If no audio tracks are 
        available, it uses the original video path. The resulting video with added subtitles is 
        saved as 'out.mkv' in the base path and rename to .mp4.
        """

        # Initialize variables
        path_video_and_audio = None
        path_join_subtitles = None

        # Check if there are any audio tracks
        if len(self.audio_tracks_path) > 0:
            # Log adding audio tracks
            console.log(f"[cyan]Add audios.")

            # Join audio tracks with the video
            path_video_and_audio = join_audios(
                video_path=self.video_track_path,
                audio_tracks=self.audio_tracks_path
            )

        # Check if there are any downloaded subtitles
        if len(self.downloaded_subtitle) > 0:
            # Log adding subtitles
            console.log(f"[cyan]Add subtitles.")

            # If no audio tracks were joined, use the original video path
            if path_video_and_audio is None:
                path_video_and_audio = self.video_track_path

            # Transcode video with subtitles
            path_join_subtitles = transcode_with_subtitles(
                path_video_and_audio,
                self.downloaded_subtitle,
                os.path.join(self.base_path, "out.mkv")
            )

        self.path_video_and_audio = path_video_and_audio
        self.path_join_subtitles = path_join_subtitles

    def cleanup_tmp(self, is_index = False):
        """Cleanup temporary files.

        This function removes temporary audio join files, the starting video file if necessary,
        and the temporary folder. It also renames the output file to the desired output filename.

        Args:
            full_path (str): The full path to the directory containing the .ts files.
            is_index (bool): To bypass audio tracks and subtitles tracks
        """

        join_output_file = None
        console.log("[cyan]Cleanup [white]...")

        # Remove audio join files
        if not is_index:
            for clean_audio_path in self.audio_tracks_path:
                remove_file(clean_audio_path.get('path'))

        # Determine the output file
        if not is_index:

            # Determine the output file
            if self.path_join_subtitles is not None:
                join_output_file = self.path_join_subtitles
                remove_file(self.path_video_and_audio)
            else:
                join_output_file = self.path_video_and_audio

            # Remove the starting video if necessary
            if self.path_join_subtitles is not None or self.path_video_and_audio is not None:
                remove_file(self.video_track_path)

            # If no join or video and audio files exist, the final output is the original video
            if self.path_join_subtitles is None and self.path_video_and_audio is None:
                join_output_file = self.video_track_path

            # Rename output file 
            os.rename(join_output_file, self.output_filename)

        # Remove the temporary folder
        if not is_index:
            remove_folder(self.base_path)
        else:
            remove_folder(os.path.join(self.base_path, "tmp"))
        
    def download_m3u8(self):
        """
        Download content from M3U8 sources including video, audio, and subtitles.
        """

        # Check if the M3U8 playlist is valid
        if self.m3u8_playlist is not None:
            logging.info(f"Download m3u8 from playlist.")

            # Fetch the M3U8 playlist content
            m3u8_playlist_text = self.__df_make_req__(self.m3u8_playlist)

            # Add full URL of the M3U8 playlist to fix next .ts without https if necessary
            class_urlFix.set_playlist(self.m3u8_playlist)

            # Collect information about the playlist
            self.manage_playlist(m3u8_playlist_text)

            # Download subtitles
            if Donwload_subtitles:
                logging.info("Download subtitles ...")
                self.manage_subtitle()

            # Download segmenets of  audio tracks
            if Download_audio:
                logging.info("Download audios ...")
                self.manage_audio()

            # Download segements of video segments
            logging.info("Download videos ...")
            self.manage_video()

            # Convert audios segments to mp4
            self.download_audios()

            # Convert video segments to mp4
            self.download_videos()

            # Add subtitles and audio to video mp4 if present
            self.add_subtitles_audios()

            # Clean up folder of all tmp folder and tmp with .ts segments folder
            if REMOVE_SEGMENTS_FOLDER:
                self.cleanup_tmp()

        else:
            logging.info(f"Download m3u8 from index.")

            # Add full URL of the M3U8 playlist to fix next .ts without https if necessary
            class_urlFix.set_playlist(self.m3u8_index)

            logging.info("Download videos ...")
            self.manage_video()

            # Convert video segments to mp4
            self.download_videos()

            # Clean up folder of all tmp folder and tmp with .ts segments folder
            if REMOVE_SEGMENTS_FOLDER:
                self.cleanup_tmp(is_index = True)
