# 17.10.24

import os
import sys
import logging


# External libraries
import httpx


# Internal utilities
from StreamingCommunity.Src.Util._jsonConfig import config_manager
from StreamingCommunity.Src.Util.console import console, Panel, Table
from StreamingCommunity.Src.Util.color import Colors
from StreamingCommunity.Src.Util.os import (
    compute_sha1_hash,
    os_manager,
    internet_manager
)

# Logic class
from ...FFmpeg import (
    print_duration_table,
    get_video_duration_s,
    join_video,
    join_audios,
    join_subtitle
)
from ...M3U8 import (
    M3U8_Parser,
    M3U8_Codec,
    M3U8_UrlFix
)
from .segments import M3U8_Segments


# Config
DOWNLOAD_SPECIFIC_AUDIO = config_manager.get_list('M3U8_DOWNLOAD', 'specific_list_audio')            
DOWNLOAD_SPECIFIC_SUBTITLE = config_manager.get_list('M3U8_DOWNLOAD', 'specific_list_subtitles')
DOWNLOAD_VIDEO = config_manager.get_bool('M3U8_DOWNLOAD', 'download_video')
DOWNLOAD_AUDIO = config_manager.get_bool('M3U8_DOWNLOAD', 'download_audio')
MERGE_AUDIO = config_manager.get_bool('M3U8_DOWNLOAD', 'merge_audio')
DOWNLOAD_SUBTITLE = config_manager.get_bool('M3U8_DOWNLOAD', 'download_sub')
MERGE_SUBTITLE = config_manager.get_bool('M3U8_DOWNLOAD', 'merge_subs')
REMOVE_SEGMENTS_FOLDER = config_manager.get_bool('M3U8_DOWNLOAD', 'cleanup_tmp_folder')
FILTER_CUSTOM_REOLUTION = config_manager.get_int('M3U8_PARSER', 'force_resolution')
GET_ONLY_LINK = config_manager.get_bool('M3U8_PARSER', 'get_only_link')


# Variable
max_timeout = config_manager.get_int("REQUESTS", "timeout")
headers_index = config_manager.get_dict('REQUESTS', 'user-agent')
m3u8_url_fixer = M3U8_UrlFix()



class PathManager:
    def __init__(self, output_filename):
        """
        Initializes the PathManager with the output filename.

        Args:
            output_filename (str): The name of the output file (should end with .mp4).
        """
        self.output_filename = output_filename
        
        # Create the base path by removing the '.mp4' extension from the output filename
        self.base_path = str(output_filename).replace(".mp4", "")
        logging.info(f"class 'PathManager'; set base path: {self.base_path}")
        
        # Define the path for a temporary directory where segments will be stored
        self.base_temp = os.path.join(self.base_path, "tmp")
        self.video_segments_path = os.path.join(self.base_temp, "video")
        self.audio_segments_path = os.path.join(self.base_temp, "audio")
        self.subtitle_segments_path = os.path.join(self.base_temp, "subtitle")

    def create_directories(self):
        """
        Creates the necessary directories for storing video, audio, and subtitle segments.
        """

        os.makedirs(self.base_temp, exist_ok=True)
        os.makedirs(self.video_segments_path, exist_ok=True)
        os.makedirs(self.audio_segments_path, exist_ok=True)
        os.makedirs(self.subtitle_segments_path, exist_ok=True)


class HttpClient:
    def __init__(self, headers: str = None):
        """
        Initializes the HttpClient with specified headers.
        """
        self.headers = headers

    def get(self, url: str):
        """
        Sends a GET request to the specified URL and returns the response as text.

        Returns:
            str: The response body as text if the request is successful, None otherwise.
        """
        logging.info(f"class 'HttpClient'; make request: {url}")
        try:
            response = httpx.get(
                url=url, 
                headers=self.headers, 
                timeout=max_timeout
            )

            response.raise_for_status()
            return response.text

        except Exception as e:
            logging.info(f"Request to {url} failed with error: {e}")
            return 404

    def get_content(self, url):
        """
        Sends a GET request to the specified URL and returns the raw response content.

        Returns:
            bytes: The response content as bytes if the request is successful, None otherwise.
        """
        logging.info(f"class 'HttpClient'; make request: {url}")
        try:
            response = httpx.get(
                url=url, 
                headers=self.headers, 
                timeout=max_timeout
            )

            response.raise_for_status()
            return response.content  # Return the raw response content

        except Exception as e:
            logging.error(f"Request to {url} failed: {response.status_code} when get content.")
            return None


class ContentExtractor:
    def __init__(self):
        """
        This class is responsible for extracting audio, subtitle, and video information from an M3U8 playlist.
        """
        pass

    def start(self, obj_parse: M3U8_Parser):
        """
        Starts the extraction process by parsing the M3U8 playlist and collecting audio, subtitle, and video data.

        Args:
            obj_parse (str): The M3U8_Parser obj of the M3U8 playlist.
        """

        self.obj_parse = obj_parse

        # Collect audio, subtitle, and video information
        self._collect_audio()
        self._collect_subtitle()
        self._collect_video()

    def _collect_audio(self):
        """
        It checks for available audio languages and the specific audio tracks to download.
        """
        logging.info(f"class 'ContentExtractor'; call _collect_audio()")

        # Collect available audio tracks and their corresponding URIs and names
        self.list_available_audio = self.obj_parse._audio.get_all_uris_and_names()
        
        # Check if there are any audio tracks available; if not, disable download
        if self.list_available_audio is not None:

            # Extract available languages from the audio tracks
            available_languages = [obj_audio.get('language') for obj_audio in self.list_available_audio]
            set_language = DOWNLOAD_SPECIFIC_AUDIO                      
            result = list(set(available_languages) & set(set_language))

            # Create a formatted table to display audio info
            if len(available_languages) > 0:
                table = Table(show_header=False, box=None)
                table.add_row(f"[cyan]Available languages:", f"[purple]{', '.join(available_languages)}")
                table.add_row(f"[red]Set audios:", f"[purple]{', '.join(set_language)}")
                table.add_row(f"[green]Downloadable:", f"[purple]{', '.join(result)}")

                console.rule("[bold green] AUDIO ", style="bold red")
                console.print(table)

        else:
            console.log("[red]Can't find a list of audios")

    def _collect_subtitle(self):
        """
        It checks for available subtitle languages and the specific subtitles to download.
        """
        logging.info(f"class 'ContentExtractor'; call _collect_subtitle()")

        # Collect available subtitles and their corresponding URIs and names
        self.list_available_subtitles = self.obj_parse._subtitle.get_all_uris_and_names()
        
        # Check if there are any subtitles available; if not, disable download
        if self.list_available_subtitles is not None:

            # Extract available languages from the subtitles
            available_languages = [obj_subtitle.get('language') for obj_subtitle in self.list_available_subtitles]
            set_language = DOWNLOAD_SPECIFIC_SUBTITLE
            result = list(set(available_languages) & set(set_language))

            # Create a formatted table to display subtitle info
            if len(available_languages) > 0:
                table = Table(show_header=False, box=None)
                table.add_row(f"[cyan]Available languages:", f"[purple]{', '.join(available_languages)}")
                table.add_row(f"[red]Set subtitles:", f"[purple]{', '.join(set_language)}")
                table.add_row(f"[green]Downloadable:", f"[purple]{', '.join(result)}")

                console.rule("[bold green] SUBTITLE ", style="bold red")
                console.print(table)

        else:
            console.log("[red]Can't find a list of subtitles")

    def _collect_video(self):
        """
        It identifies the best video quality and displays relevant information to the user.
        """
        logging.info(f"class 'ContentExtractor'; call _collect_video()")

        # Collect custom quality video if a specific resolution is set
        if FILTER_CUSTOM_REOLUTION != -1:
            self.m3u8_index, video_res = self.obj_parse._video.get_custom_uri(y_resolution=FILTER_CUSTOM_REOLUTION)

        # Otherwise, get the best available video quality
        self.m3u8_index, video_res = self.obj_parse._video.get_best_uri()
        self.codec: M3U8_Codec = self.obj_parse.codec

        # List all available resolutions
        tuple_available_resolution = self.obj_parse._video.get_list_resolution()
        list_available_resolution = [str(resolution[0]) + "x" + str(resolution[1]) for resolution in tuple_available_resolution]
        logging.info(f"M3U8 index selected: {self.m3u8_index}, with resolution: {video_res}")

        # Create a formatted table to display video info
        table = Table(show_header=False, box=None)
        table.add_row(f"[cyan]Available resolutions:", f"[purple]{', '.join(list_available_resolution)}")
        table.add_row(f"[green]Downloadable:", f"[purple]{video_res[0]}x{video_res[1]}")

        if self.codec is not None:
            if config_manager.get_bool("M3U8_CONVERSION", "use_codec"):
                table.add_row(f"[green]Codec:", f"([green]'v'[white]: [yellow]{self.codec.video_codec_name}[white] ([green]b[white]: [yellow]{self.codec.video_bitrate // 1000}k[white]), [green]'a'[white]: [yellow]{self.codec.audio_codec_name}[white] ([green]b[white]: [yellow]{self.codec.audio_bitrate // 1000}k[white]))")
            else:
                table.add_row(f"[green]Codec:", "[purple]copy")

        console.rule("[bold green] VIDEO ", style="bold red")
        console.print(table)
        print("")

        # Fix the URL if it does not include the full protocol
        if "http" not in self.m3u8_index:

            # Generate the full URL
            self.m3u8_index = m3u8_url_fixer.generate_full_url(self.m3u8_index)
            logging.info(f"Generated index URL: {self.m3u8_index}")

            # Check if a valid HTTPS URL is obtained
            if self.m3u8_index is not None and "https" in self.m3u8_index:
                #console.print(f"[cyan]Found m3u8 index [white]=> [red]{self.m3u8_index}")
                print()

            else:
                logging.error("[download_m3u8] Can't find a valid m3u8 index")
                raise ValueError("Invalid m3u8 index URL")
            

class DownloadTracker:
    def __init__(self, path_manager: PathManager):
        """
        Initializes the DownloadTracker with paths for audio, subtitle, and video segments.

        Args:
            path_manager (PathManager): An instance of the PathManager class to manage file paths.
        """

        # Initialize lists to track downloaded audio, subtitles, and video
        self.downloaded_audio = []
        self.downloaded_subtitle = []
        self.downloaded_video = []

        self.video_segment_path = path_manager.video_segments_path
        self.audio_segments_path = path_manager.audio_segments_path
        self.subtitle_segments_path = path_manager.subtitle_segments_path

    def add_video(self, available_video):
        """
        Adds a single video to the list of downloaded videos.

        Args:
            available_video (str): The URL of the video to be downloaded.
        """
        logging.info(f"class 'DownloadTracker'; call add_video() with parameter: {available_video}")

        self.downloaded_video.append({
            'type': 'video',
            'url': available_video,
            'path': os.path.join(self.video_segment_path, "0.ts")
        })

    def add_audio(self, list_available_audio):
        """
        Adds available audio tracks to the list of downloaded audio.

        Args:
            list_available_audio (list): A list of available audio track objects.
        """
        logging.info(f"class 'DownloadTracker'; call add_audio() with parameter: {list_available_audio}")

        for obj_audio in list_available_audio:

            # Check if specific audio languages are set for download
            if len(DOWNLOAD_SPECIFIC_AUDIO) > 0:

                # Skip this audio track if its language is not in the specified list
                if obj_audio.get('language') not in DOWNLOAD_SPECIFIC_AUDIO:
                    continue

            # Construct the full path for the audio segment directory
            full_path_audio = os.path.join(self.audio_segments_path, obj_audio.get('language'))

            # Append the audio information to the downloaded audio list
            self.downloaded_audio.append({
                'type': 'audio',
                'url': obj_audio.get('uri'),
                'language': obj_audio.get('language'),
                'path': os.path.join(full_path_audio, "0.ts")
            })

    def add_subtitle(self, list_available_subtitles):
        """
        Adds available subtitles to the list of downloaded subtitles.

        Args:
            list_available_subtitles (list): A list of available subtitle objects.
        """
        logging.info(f"class 'DownloadTracker'; call add_subtitle() with parameter: {list_available_subtitles}")

        for obj_subtitle in list_available_subtitles:

            # Check if specific subtitle languages are set for download
            if len(DOWNLOAD_SPECIFIC_SUBTITLE) > 0:

                # Skip this subtitle if its language is not in the specified list
                if obj_subtitle.get('language') not in DOWNLOAD_SPECIFIC_SUBTITLE:
                    continue
            
            sub_language = obj_subtitle.get('language')
            
            # Construct the full path for the subtitle file
            sub_full_path = os.path.join(self.subtitle_segments_path, sub_language + ".vtt")

            self.downloaded_subtitle.append({
                'type': 'sub',
                'url': obj_subtitle.get('uri'),
                'language': obj_subtitle.get('language'),
                'path': sub_full_path
            })


class ContentDownloader:
    def __init__(self):
        """
        Initializes the ContentDownloader class.

        Attributes:
            expected_real_time (float): Expected real-time duration of the video download.
        """
        self.expected_real_time = None

    def download_video(self, downloaded_video):
        """
        Downloads the video if it doesn't already exist.

        Args:
            downloaded_video (list): A list containing information about the video to download.
        """
        logging.info(f"class 'ContentDownloader'; call download_video() with parameter: {downloaded_video}")

        # Check if the video file already exists
        if not os.path.exists(downloaded_video[0].get('path')):
            folder_name = os.path.dirname(downloaded_video[0].get('path'))

            # Create an instance of M3U8_Segments to handle video segments download
            video_m3u8 = M3U8_Segments(downloaded_video[0].get('url'), folder_name)

            # Get information about the video segments (e.g., duration, ts files to download)
            video_m3u8.get_info()

            # Store the expected real-time duration of the video
            self.expected_real_time = video_m3u8.expected_real_time

            # Download the video streams and print status
            video_m3u8.download_streams(f"{Colors.MAGENTA}video")

            # Print duration information of the downloaded video
            #print_duration_table(downloaded_video[0].get('path'))

        else:
            console.log("[cyan]Video [red]already exists.")

    def download_audio(self, downloaded_audio):
        """
        Downloads audio tracks if they don't already exist.

        Args:
            downloaded_audio (list): A list containing information about audio tracks to download.
        """
        logging.info(f"class 'ContentDownloader'; call download_audio() with parameter: {downloaded_audio}")

        for obj_audio in downloaded_audio:
            folder_name = os.path.dirname(obj_audio.get('path'))

            # Check if the audio file already exists
            if not os.path.exists(obj_audio.get('path')):

                # Create an instance of M3U8_Segments to handle audio segments download
                audio_m3u8 = M3U8_Segments(obj_audio.get('url'), folder_name)

                # Get information about the audio segments (e.g., duration, ts files to download)
                audio_m3u8.get_info()

                # Download the audio segments and print status
                audio_m3u8.download_streams(f"{Colors.MAGENTA}audio {Colors.RED}{obj_audio.get('language')}")

                # Print duration information of the downloaded audio
                #print_duration_table(obj_audio.get('path'))

            else:
                console.log(f"[cyan]Audio [white]([green]{obj_audio.get('language')}[white]) [red]already exists.")

    def download_subtitle(self, downloaded_subtitle):
        """
        Downloads subtitle files if they don't already exist.

        Args:
            downloaded_subtitle (list): A list containing information about subtitles to download.
        """
        logging.info(f"class 'ContentDownloader'; call download_subtitle() with parameter: {downloaded_subtitle}")

        for obj_subtitle in downloaded_subtitle:
            sub_language = obj_subtitle.get('language')

            # Check if the subtitle file already exists
            if os.path.exists(obj_subtitle.get("path")):
                console.log(f"[cyan]Subtitle [white]([green]{sub_language}[white]) [red]already exists.")
                continue  # Skip to the next subtitle if it exists

            # Parse the M3U8 file to get the subtitle URI
            m3u8_sub_parser = M3U8_Parser()
            m3u8_sub_parser.parse_data(
                uri=obj_subtitle.get('uri'),
                raw_content=httpx.get(obj_subtitle.get('url')).text  # Fetch subtitle content
            )

            # Print the status of the subtitle download
            #console.print(f"[cyan]Downloading subtitle: [red]{sub_language.lower()}")

            # Write the content to the specified file
            with open(obj_subtitle.get("path"), "wb") as f:
                f.write(HttpClient().get_content(m3u8_sub_parser.subtitle[-1]))


class ContentJoiner:
    def __init__(self, path_manager):
        """
        Initializes the ContentJoiner class.

        Args:
            path_manager (PathManager): An instance of PathManager to manage output paths.
        """
        self.path_manager: PathManager = path_manager

    def setup(self, downloaded_video, downloaded_audio, downloaded_subtitle, codec = None):
        """
        Sets up the content joiner with downloaded media files.

        Args:
            downloaded_video (list): List of downloaded video information.
            downloaded_audio (list): List of downloaded audio information.
            downloaded_subtitle (list): List of downloaded subtitle information.
        """
        self.downloaded_video = downloaded_video
        self.downloaded_audio = downloaded_audio
        self.downloaded_subtitle = downloaded_subtitle
        self.codec = codec
        
        # Initialize flags to check if media is available
        self.converted_out_path = None
        self.there_is_video = len(downloaded_video) > 0
        self.there_is_audio = len(downloaded_audio) > 0
        self.there_is_subtitle = len(downloaded_subtitle) > 0

        if self.there_is_audio or self.there_is_subtitle:

            # Display the status of available media
            table = Table(show_header=False, box=None)

            table.add_row(f"[green]Video - audio", f"[yellow]{self.there_is_audio}")
            table.add_row(f"[green]Video - Subtitle", f"[yellow]{self.there_is_subtitle}")

            print("")
            console.rule("[bold green] JOIN ", style="bold red")
            console.print(table)
            print("")

        # Start the joining process
        self.conversione()

    def conversione(self):
        """
        Handles the joining of video, audio, and subtitles based on availability.
        """

        # Join audio and video if audio is available
        if self.there_is_audio:
            if MERGE_AUDIO:

                # Join video with audio tracks
                self.converted_out_path = self._join_video_audio()

            else:

                # Process each available audio track
                for obj_audio in self.downloaded_audio:
                    language = obj_audio.get('language')
                    path = obj_audio.get('path')

                    # Set the new path for regular audio
                    new_path = self.path_manager.output_filename.replace(".mp4", f"_{language}.mp4")

                    try:

                        # Rename the audio file to the new path
                        os.rename(path, new_path)
                        logging.info(f"Audio moved to {new_path}")
                    
                    except Exception as e:
                        logging.error(f"Failed to move audio {path} to {new_path}: {e}")

                # Convert video if available
                if self.there_is_video:
                    self.converted_out_path = self._join_video()

        # If no audio but video is available, join video
        else:
            if self.there_is_video:
                self.converted_out_path = self._join_video()

        # Join subtitles if available
        if self.there_is_subtitle:
            if MERGE_SUBTITLE:
                if self.converted_out_path is not None:
                    self.converted_out_path = self._join_video_subtitles(self.converted_out_path)

            else:

                # Process each available subtitle track
                for obj_sub in self.downloaded_subtitle:
                    language = obj_sub.get('language')
                    path = obj_sub.get('path')
                    forced = 'forced' in language

                    # Adjust the language name and set the new path based on forced status
                    if forced:
                        language = language.replace("forced-", "")
                        new_path = self.path_manager.output_filename.replace(".mp4", f".{language}.forced.vtt")
                    else:
                        new_path = self.path_manager.output_filename.replace(".mp4", f".{language}.vtt")
                    
                    try:
                        # Rename the subtitle file to the new path
                        os.rename(path, new_path)
                        logging.info(f"Subtitle moved to {new_path}")
                    
                    except Exception as e:
                        logging.error(f"Failed to move subtitle {path} to {new_path}: {e}")

    def _join_video(self):
        """
        Joins video segments into a single video file.

        Returns:
            str: The path to the joined video file.
        """
        path_join_video = os.path.join(self.path_manager.base_path, "v_v.mp4")
        logging.info(f"JOIN video path: {path_join_video}")

        # Check if the joined video file already exists
        if not os.path.exists(path_join_video):

            # Set codec to None if not defined in class
            #if not hasattr(self, 'codec'):
            #    self.codec = None

            # Join the video segments into a single video file
            join_video(
                video_path=self.downloaded_video[0].get('path'),
                out_path=path_join_video,
                codec=self.codec
            )

        else:
            console.log("[red]Output join video already exists.")

        return path_join_video

    def _join_video_audio(self):
        """
        Joins video segments with audio tracks into a single video with audio file.

        Returns:
            str: The path to the joined video with audio file.
        """
        path_join_video_audio = os.path.join(self.path_manager.base_path, "v_a.mp4")
        logging.info(f"JOIN audio path: {path_join_video_audio}")

        # Check if the joined video with audio file already exists
        if not os.path.exists(path_join_video_audio):

            # Set codec to None if not defined in class
            #if not hasattr(self, 'codec'):
            #    self.codec = None

            # Join the video with audio segments
            join_audios(
                video_path=self.downloaded_video[0].get('path'),
                audio_tracks=self.downloaded_audio,
                out_path=path_join_video_audio,
                codec=self.codec
            )

        else:
            console.log("[red]Output join video and audio already exists.")

        return path_join_video_audio

    def _join_video_subtitles(self, input_path):
        """
        Joins subtitles with the video.

        Args:
            input_path (str): The path to the video file to which subtitles will be added.

        Returns:
            str: The path to the video with subtitles file.
        """
        path_join_video_subtitle = os.path.join(self.path_manager.base_path, "v_s.mp4")
        logging.info(f"JOIN subtitle path: {path_join_video_subtitle}")

        # Check if the video with subtitles file already exists
        if not os.path.exists(path_join_video_subtitle):

            # Join the video with subtitles
            join_subtitle(
                input_path,
                self.downloaded_subtitle,
                path_join_video_subtitle
            )

        return path_join_video_subtitle


class HLS_Downloader:
    def __init__(self, output_filename: str=None, m3u8_playlist: str=None, m3u8_index: str=None, is_playlist_url: bool=True, is_index_url: bool=True):
        """
        Initializes the HLS_Downloader class.

        Args:
            output_filename (str): The desired output filename for the downloaded content.
            m3u8_playlist (str): The URL or content of the m3u8 playlist.
            m3u8_index (str): The index URL for m3u8 streams.
            is_playlist_url (bool): Flag indicating if the m3u8_playlist is a URL.
            is_index_url (bool): Flag indicating if the m3u8_index is a URL.
        """
        if ((m3u8_playlist == None or m3u8_playlist == "") and output_filename is None) or ((m3u8_index == None or m3u8_index == "") and output_filename is None):
            logging.info(f"class 'HLS_Downloader'; call __init__(); no parameter")
            sys.exit(0)

        self.output_filename = self._generate_output_filename(output_filename, m3u8_playlist, m3u8_index)
        self.path_manager = PathManager(self.output_filename)
        self.download_tracker = DownloadTracker(self.path_manager)
        self.content_extractor = ContentExtractor()
        self.content_downloader = ContentDownloader()
        self.content_joiner = ContentJoiner(self.path_manager)

        self.m3u8_playlist = m3u8_playlist
        self.m3u8_index = m3u8_index
        self.is_playlist_url = is_playlist_url
        self.is_index_url = is_index_url
        self.expected_real_time = None
        self.instace_parserClass = M3U8_Parser()

        self.request_m3u8_playlist = None
        self.request_m3u8_index = None
        if (m3u8_playlist == None or m3u8_playlist == ""):
            self.request_m3u8_index = HttpClient().get(self.m3u8_index)
        if (m3u8_index == None or m3u8_index == ""):
            self.request_m3u8_playlist = HttpClient().get(self.m3u8_playlist)

    def _generate_output_filename(self, output_filename, m3u8_playlist, m3u8_index):
        """
        Generates a valid output filename based on provided parameters.

        Args:
            output_filename (str): The desired output filename.
            m3u8_playlist (str): The m3u8 playlist URL or content.
            m3u8_index (str): The m3u8 index URL.

        Returns:
            str: The generated output filename.
        """
        root_path = config_manager.get('DEFAULT', 'root_path')  
        new_filename = None
        new_folder = os.path.join(root_path, "undefined")
        logging.info(f"class 'HLS_Downloader'; call _generate_output_filename(); destination folder: {new_folder}")

        # Auto-generate output file name if not present
        if (output_filename is None) or ("mp4" not in output_filename):
            if m3u8_playlist is not None:
                new_filename = os.path.join(new_folder, compute_sha1_hash(m3u8_playlist) + ".mp4")
            else:
                new_filename = os.path.join(new_folder, compute_sha1_hash(m3u8_index) + ".mp4")

        else:

            # Check if output_filename contains a folder path
            folder, base_name = os.path.split(output_filename) 
            
            # If no folder is specified, default to 'undefined'
            if not folder:
                folder = new_folder

            # Sanitize base name and folder
            folder = os_manager.get_sanitize_path(folder)
            base_name = os_manager.get_sanitize_file(base_name)
            os_manager.create_path(folder)

            # Parse to only ASCII for compatibility across platforms
            new_filename = os.path.join(folder, base_name)

        logging.info(f"class 'HLS_Downloader'; call _generate_output_filename(); return path: {new_filename}")
        return new_filename
    
    def start(self):
        """
        Initiates the downloading process. Checks if the output file already exists and proceeds with processing the playlist or index.
        """            
        if os.path.exists(self.output_filename):
            console.log("[red]Output file already exists.")
            return 400
        
        self.path_manager.create_directories()
        
        # Determine whether to process a playlist or index
        if self.m3u8_playlist:
            if self.m3u8_playlist is not None:
                if self.request_m3u8_playlist != 404:
                    logging.info(f"class 'HLS_Downloader'; call start(); parse m3u8 data")

                    self.instace_parserClass.parse_data(uri=self.m3u8_playlist, raw_content=self.request_m3u8_playlist)
                    is_masterPlaylist = self.instace_parserClass.is_master_playlist

                    # Check if it's a real master playlist
                    if is_masterPlaylist:
                        if not GET_ONLY_LINK:
                            r_proc = self._process_playlist()

                            if r_proc == 404:
                                return 404
                            else:
                                return None    
                        
                        else:
                            return {
                                'path': self.output_filename,
                                'url': self.m3u8_playlist
                            }
                    
                    else:
                        console.log("[red]Error: URL passed to M3U8_Parser is an index playlist; expected a master playlist. Crucimorfo strikes again!")
                else:
                    console.log(f"[red]Error: m3u8_playlist failed request for: {self.m3u8_playlist}")
            else:
                console.log("[red]Error: m3u8_playlist is None")

        elif self.m3u8_index:
            if self.m3u8_index is not None:
                if self.request_m3u8_index != 404:
                    logging.info(f"class 'HLS_Downloader'; call start(); parse m3u8 data")

                    self.instace_parserClass.parse_data(uri=self.m3u8_index, raw_content=self.request_m3u8_index)
                    is_masterPlaylist = self.instace_parserClass.is_master_playlist

                    # Check if it's a real index playlist
                    if not is_masterPlaylist:
                        if not GET_ONLY_LINK:
                            self._process_index()
                            return None

                        else:
                            return {
                                'path': self.output_filename,
                                'url': self.m3u8_index
                            }
                    
                    else:
                        console.log("[red]Error: URL passed to M3U8_Parser is an master playlist; expected a index playlist. Crucimorfo strikes again!")
                else:
                    console.log("[red]Error: m3u8_index failed request")
            else:
                console.log("[red]Error: m3u8_index is None")

    def _clean(self, out_path: str) -> None:
        """
        Cleans up temporary files and folders after downloading and processing.

        Args:
            out_path (str): The path of the output file to be cleaned up.
        """
        def dict_to_seconds(d):
            """Converts a dictionary of time components to total seconds."""
            if d is not None:
                return d['h'] * 3600 + d['m'] * 60 + d['s']
            return 0

        # Check if the final output file exists
        logging.info(f"Check if end file converted exists: {out_path}")
        if out_path is None or not os.path.isfile(out_path):
            logging.error("Video file converted does not exist.")
            sys.exit(0)

        # Rename the output file to the desired output filename if it does not already exist
        if not os.path.exists(self.output_filename):

            # Rename the converted file to the specified output filename
            os.rename(out_path, self.output_filename)

            # Get duration information for the output file
            end_output_time = print_duration_table(self.output_filename, description=False, return_string=False)

            # Calculate file size and duration for reporting
            formatted_size = internet_manager.format_file_size(os.path.getsize(self.output_filename))
            formatted_duration = print_duration_table(self.output_filename, description=False, return_string=True)
            
            expected_real_seconds = dict_to_seconds(self.content_downloader.expected_real_time)
            end_output_seconds = dict_to_seconds(end_output_time)

            # Check if the downloaded content is complete based on expected duration
            if expected_real_seconds is not None:
                missing_ts = not (expected_real_seconds - 3 <= end_output_seconds <= expected_real_seconds + 3)
            else:
                missing_ts = "Undefined"

            # Second check for missing segments
            if not missing_ts:
                if get_video_duration_s(self.output_filename) < int(expected_real_seconds) - 5:
                    missing_ts = True

            # Prepare the report panel content
            print("")
            panel_content = (
                f"[bold green]Download completed![/bold green]\n"
                f"[cyan]File size: [bold red]{formatted_size}[/bold red]\n"
                f"[cyan]Duration: [bold]{formatted_duration}[/bold]\n"
                f"[cyan]Missing TS: [bold red]{missing_ts}[/bold red]"
            )

            # Display the download completion message
            console.print(Panel(
                panel_content,
                title=f"{os.path.basename(self.output_filename.replace('.mp4', ''))}",
                border_style="green"
            ))

            # Handle missing segments
            if missing_ts:
                os.rename(self.output_filename, self.output_filename.replace(".mp4", "_failed.mp4"))

            # Delete all temporary files except for the output file
            os_manager.remove_files_except_one(self.path_manager.base_path, os.path.basename(self.output_filename.replace(".mp4", "_failed.mp4")))

            # Remove the base folder if specified
            if REMOVE_SEGMENTS_FOLDER:
                os_manager.remove_folder(self.path_manager.base_path)

        else:
            logging.info("Video file converted already exists.")

    def _valida_playlist(self):
        """
        Validates the m3u8 playlist content, saves it to a temporary file, and collects playlist information.
        """
        logging.info("class 'HLS_Downloader'; call _valida_playlist()")

        # Retrieve the m3u8 playlist content
        if self.is_playlist_url: 
            if self.request_m3u8_playlist  != 404:
                m3u8_playlist_text = self.request_m3u8_playlist
                m3u8_url_fixer.set_playlist(self.m3u8_playlist)

            else:
                logging.info(f"class 'HLS_Downloader'; call _process_playlist(); return 404")
                return 404

        else:
            m3u8_playlist_text = self.m3u8_playlist

        # Check if the m3u8 content is valid
        if m3u8_playlist_text is None:
            console.log("[red]Playlist m3u8 to download is empty.")
            sys.exit(0) 

        # Save the m3u8 playlist text to a temporary file
        open(os.path.join(self.path_manager.base_temp, "playlist.m3u8"), "w+", encoding="utf-8").write(m3u8_playlist_text)

        # Collect information about the playlist
        if self.is_playlist_url:
            self.content_extractor.start(self.instace_parserClass)
        else:
            self.content_extractor.start("https://fake.com", m3u8_playlist_text)

    def _process_playlist(self):
        """
        Processes the m3u8 playlist to download video, audio, and subtitles.
        """
        self._valida_playlist()

        # Add downloaded elements to the tracker
        self.download_tracker.add_video(self.content_extractor.m3u8_index)
        self.download_tracker.add_audio(self.content_extractor.list_available_audio)
        self.download_tracker.add_subtitle(self.content_extractor.list_available_subtitles)

        # Download each type of content
        if DOWNLOAD_VIDEO and len(self.download_tracker.downloaded_video) > 0:
            self.content_downloader.download_video(self.download_tracker.downloaded_video)
        if DOWNLOAD_AUDIO and len(self.download_tracker.downloaded_audio) > 0:
            self.content_downloader.download_audio(self.download_tracker.downloaded_audio)
        if DOWNLOAD_SUBTITLE and len(self.download_tracker.downloaded_subtitle) > 0:
            self.content_downloader.download_subtitle(self.download_tracker.downloaded_subtitle)

        # Join downloaded content
        self.content_joiner.setup(self.download_tracker.downloaded_video, self.download_tracker.downloaded_audio, self.download_tracker.downloaded_subtitle, self.content_extractor.codec)

        # Clean up temporary files and directories
        self._clean(self.content_joiner.converted_out_path)
        
    def _process_index(self):
        """
        Processes the m3u8 index to download only video.
        """
        m3u8_url_fixer.set_playlist(self.m3u8_index)

        # Download video
        self.download_tracker.add_video(self.m3u8_index)
        self.content_downloader.download_video(self.download_tracker.downloaded_video)
        
        # Join video
        self.content_joiner.setup(self.download_tracker.downloaded_video, [], [])

        # Clean up temporary files and directories
        self._clean(self.content_joiner.converted_out_path)
