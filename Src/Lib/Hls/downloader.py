# 5.01.24

import os
import sys
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


# External libraries
from Src.Lib.Request import requests
from unidecode import unidecode


# Internal utilities
from Src.Util.headers import get_headers
from Src.Util._jsonConfig import config_manager
from Src.Util.console import console, Panel
from Src.Util.color import Colors
from Src.Util.os import (
    remove_folder,
    delete_files_except_one,
    compute_sha1_hash,
    format_size,
    create_folder, 
    reduce_base_name, 
    remove_special_characters,
    can_create_file
)


# Logic class
from ..FFmpeg import (
    print_duration_table,
    join_video,
    join_audios,
    join_subtitle
)
from ..M3U8 import (
    M3U8_Parser,
    M3U8_Codec,
    M3U8_UrlFix
)
from .segments import M3U8_Segments
from ..E_Table import report_table


# Config
DOWNLOAD_SPECIFIC_AUDIO = config_manager.get_list('M3U8_DOWNLOAD', 'specific_list_audio')            
DOWNLOAD_SPECIFIC_SUBTITLE = config_manager.get_list('M3U8_DOWNLOAD', 'specific_list_subtitles')
DOWNLOAD_VIDEO = config_manager.get_bool('M3U8_DOWNLOAD', 'download_video')
DOWNLOAD_AUDIO = config_manager.get_bool('M3U8_DOWNLOAD', 'download_audio')
DOWNLOAD_SUB = config_manager.get_bool('M3U8_DOWNLOAD', 'download_sub')
REMOVE_SEGMENTS_FOLDER = config_manager.get_bool('M3U8_DOWNLOAD', 'cleanup_tmp_folder')
FILTER_CUSTOM_REOLUTION = config_manager.get_int('M3U8_PARSER', 'force_resolution')
CREATE_REPORT = config_manager.get_bool('M3U8_DOWNLOAD', 'create_report')


# Variable
headers_index = config_manager.get_dict('REQUESTS', 'index')


    
class Downloader():
    def __init__(self, output_filename: str = None, m3u8_playlist:str = None, m3u8_index:str = None):

        """
        Initialize the Downloader object.

        Args:
            - output_filename (str): Output filename for the downloaded content.
            - m3u8_playlist (str, optional): URL to the main M3U8 playlist or text.
            - m3u8_playlist (str, optional): URL to the main M3U8 index. ( NOT TEXT )
        """

        self.m3u8_playlist = m3u8_playlist
        self.m3u8_index = m3u8_index
        self.output_filename = output_filename

        # Auto generate out file name if not present
        if output_filename == None:
            if m3u8_playlist != None:
                self.output_filename = os.path.join("missing", compute_sha1_hash(m3u8_playlist))
            else:
                self.output_filename = os.path.join("missing", compute_sha1_hash(m3u8_index))

        else:
            folder, base_name = os.path.split(self.output_filename)                             # Split file_folder output
            base_name = reduce_base_name(remove_special_characters(base_name))   # Remove special char
            create_folder(folder)                                                               # Create folder and check if exist
            if not can_create_file(base_name):                                                  # Check if folder file name can be create
                logging.error("Invalid mp4 name.")
                sys.exit(0)

            self.output_filename = os.path.join(folder, base_name)
            self.output_filename = unidecode(self.output_filename)

        logging.info(f"Output filename: {self.output_filename}")

        # Initialize temp base path
        self.base_path = os.path.join(str(self.output_filename).replace(".mp4", ""))
        self.video_segments_path = os.path.join(self.base_path, "tmp", "video")
        self.audio_segments_path = os.path.join(self.base_path, "tmp", "audio")
        self.subtitle_segments_path = os.path.join(self.base_path, "tmp", "subtitle")
        logging.info(f"Output base path: {self.base_path}")

        # Create temp folder
        os.makedirs(self.video_segments_path, exist_ok=True)
        os.makedirs(self.audio_segments_path, exist_ok=True)
        os.makedirs(self.subtitle_segments_path, exist_ok=True)

        # Track subtitle, audio donwload
        self.downloaded_audio = []
        self.downloaded_subtitle = []
        self.downloaded_video = []

        # Path converted ts files
        self.path_video_audio = None
        self.path_video_subtitle = None

        # Class
        self.m3u8_url_fixer = M3U8_UrlFix()
 
    def __df_make_req__(self, url: str) -> str:
        """
        Make a request to get text from the provided URL to test if index or m3u8 work correcly.

        Args:
            - url (str): The URL to make the request to.

        Returns:
            str: The text content of the response.
        """

        try:

            # Send a GET request to the provided URL
            logging.info(f"Test url: {url}")
            headers_index['user-agent'] = get_headers()
            response = requests.get(url, headers=headers_index)

            if response.ok:
                return response.text
            
            else:
                logging.error(f"Test request to {url} failed with status code: {response.status_code}")
                return None

        except Exception as e:
            logging.error(f"An unexpected error occurred with test request: {e}")
            return None
        
    def __manage_playlist__(self, m3u8_playlist_text):
        """
        Parses the M3U8 playlist to extract information about keys, playlists, subtitles, etc.

        Args:
            - m3u8_playlist_text (str): The text content of the M3U8 playlist.
        """

        # Create an instance of the M3U8_Parser class
        obj_parse = M3U8_Parser()

        # Extract information about the M3U8 playlist
        obj_parse.parse_data(
            uri=self.m3u8_playlist, 
            raw_content=m3u8_playlist_text
        )


        # Collect available audio tracks and default audio track
        self.list_available_audio = obj_parse._audio.get_all_uris_and_names()
        self.default_audio = obj_parse._audio.get_default_uri()
        logging.info(f"List audios available: {self.list_available_audio}")
        logging.info(f"Default audio: {self.default_audio}")

        # Check if there is some audios, else disable download
        if self.list_available_audio != None:
            console.log(f"[cyan]Find audios [white]=> [red]{[obj_audio.get('language') for obj_audio in self.list_available_audio]}")
        else:
            console.log("[red]Cant find a list of audios")


        # Collect available subtitles and default subtitle
        self.list_available_subtitles = obj_parse._subtitle.get_all_uris_and_names()
        self.default_subtitle = obj_parse._subtitle.get_default_uri()
        logging.info(f"List subtitles available: {self.list_available_subtitles}")
        logging.info(f"Default subtitle: {self.default_subtitle}")

        # Check if there is some subtitles, else disable download
        if self.list_available_subtitles != None:
            console.log(f"[cyan]Find subtitles [white]=> [red]{[obj_sub.get('language') for obj_sub in self.list_available_subtitles]}")
        else:
            console.log("[red]Cant find a list of audios")


        # Collect custom quality video and list of resolution
        if FILTER_CUSTOM_REOLUTION != -1:
            self.m3u8_index, video_res = obj_parse._video.get_custom_uri(y_resolution=FILTER_CUSTOM_REOLUTION)

        # Check if custom uri work, and get best uri if dont work
        if self.m3u8_index is None:
            self.m3u8_index, video_res = obj_parse._video.get_best_uri()

        list_available_resolution = obj_parse._video.get_list_resolution()
        logging.info(f"M3U8 index select: {self.m3u8_index}, with resolution: {video_res}")

        # Get URI of the best quality and codecs parameters
        console.log(f"[cyan]Find resolution [white]=> [red]{sorted(list_available_resolution, reverse=True)}")

        # Fix URL if it is not complete with http:\\site_name.domain\...
        if "http" not in self.m3u8_index:

            # Generate full URL
            self.m3u8_index = self.m3u8_url_fixer.generate_full_url(self.m3u8_index)
            logging.info(f"Generate index url: {self.m3u8_index}")

            # Check if a valid HTTPS URL is obtained
            if self.m3u8_index is not None and "https" in self.m3u8_index:
                console.log(f"[cyan]Found m3u8 index [white]=> [red]{self.m3u8_index}")
            else:
                logging.error("[download_m3u8] Can't find a valid m3u8 index")
                raise

        # Get obj codec
        self.codec: M3U8_Codec = obj_parse.codec
        logging.info(f"Find codec: {self.codec}")

        if self.codec is not None:
            console.log(f"[cyan]Find codec [white]=> ([green]'v'[white]: [yellow]{self.codec.video_codec_name}[white], [green]'a'[white]: [yellow]{self.codec.audio_codec_name}[white], [green]'b'[white]: [yellow]{self.codec.bandwidth})")

    def __donwload_video__(self, server_ip: list = None):
        """
        Downloads and manages video segments.

        This method downloads video segments if necessary and updates
        the list of downloaded video segments.

        Args:
            - server_ip (list): A list of IP addresses to use in requests.
        """

        # Construct full path for the video segment directory
        full_path_video = self.video_segments_path

        # Add the video segment directory to the list of downloaded video segments
        self.downloaded_video.append({
            'path': os.path.join(self.video_segments_path, "0.ts")
        })
        logging.info(f"TS video path download: {os.path.join(self.video_segments_path, '0.ts')}")

        if not os.path.exists(self.downloaded_video[-1].get('path')):

            # Create an instance of M3U8_Segments to handle video segments
            video_m3u8 = M3U8_Segments(self.m3u8_index, full_path_video)
            video_m3u8.add_server_ip(server_ip)

            # Get information about the video segments
            video_m3u8.get_info()
            
            # Download the video segments
            video_m3u8.download_streams(f"{Colors.MAGENTA}video")

        else:
            console.log("[cyan]Video [red]already exists.")

    def __donwload_audio__(self, server_ip: list = None):
        """
        Downloads and manages audio segments.

        This method iterates over available audio tracks, downloads them if necessary, and updates
        the list of downloaded audio tracks.

        Args:
            - server_ip (list): A list of IP addresses to use in requests.
        """

        # Iterate over each available audio track
        for obj_audio in self.list_available_audio:

            # Check if there is custom subtitles to download
            if len(DOWNLOAD_SPECIFIC_AUDIO) > 0:

                # Check if language in list
                if obj_audio.get('language') not in DOWNLOAD_SPECIFIC_AUDIO:
                    continue

            # Construct full path for the audio segment directory
            full_path_audio = os.path.join(self.audio_segments_path, obj_audio.get('language'))

            self.downloaded_audio.append({
                'language': obj_audio.get('language'),
                'path': os.path.join(full_path_audio, "0.ts")
            })
            logging.info(f"TS audio path download: {os.path.join(full_path_audio, '0.ts')}")

            # Check if the audio segment directory already exists
            if not os.path.exists(self.downloaded_audio[-1].get('path')):

                # If the audio segment directory doesn't exist, download audio segments
                audio_m3u8 = M3U8_Segments(obj_audio.get('uri'), full_path_audio)
                audio_m3u8.add_server_ip(server_ip)

                # Get information about the audio segments
                audio_m3u8.get_info()
                
                # Download the audio segments
                audio_m3u8.download_streams(f"{Colors.MAGENTA}audio {Colors.RED}{obj_audio.get('language')}")

            else:
                console.log(f"[cyan]Audio [white]([green]{obj_audio.get('language')}[white]) [red]already exists.")

    def __save_subtitle_content(self, uri: str, path: str) -> None:
        """
        Download subtitle content from the provided URI and save it to the specified path.

        Args:
            - uri (str): The URI from which to download the subtitle content.
            - path (str): The path where the subtitle content will be saved.
        """

        # Send a GET request to download the subtitle content
        response = requests.get(uri)

        if response.ok:

            # Write the content to the specified file
            with open(path, "wb") as f:
                f.write(response.content)

        else:
            logging.error(f"Failed to download subtitle from {uri}. Status code: {response.status_code}")

    def __download_subtitle__(self) -> None:
        """
        Download subtitles for available languages asynchronously and save them to disk.
        """

        # Use ThreadPoolExecutor to download subtitles concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            for obj_subtitle in self.list_available_subtitles:

                # Check if the language should be downloaded based on configuration
                if obj_subtitle.get('language') not in DOWNLOAD_SPECIFIC_SUBTITLE:
                    continue
                
                sub_language = obj_subtitle.get('language')
                sub_full_path = os.path.join(self.subtitle_segments_path, sub_language + ".vtt")
                logging.info(f"VTT subtitle path download: {sub_full_path}")

                # Add the subtitle to the list of downloaded subtitles
                self.downloaded_subtitle.append({
                    'name': obj_subtitle.get('name').split(" ")[0],
                    'path': sub_full_path
                })
                
                # Check if the subtitle file already exists
                if os.path.exists(sub_full_path):
                    console.log(f"[cyan]Subtitle [white]([green]{sub_language}[wite]) [red]already exists.")
                    continue

                # Parse the M3U8 file to get the subtitle URI
                m3u8_sub_parser = M3U8_Parser()
                m3u8_sub_parser.parse_data(
                    uri = obj_subtitle.get('uri'),
                    raw_content = requests.get(obj_subtitle.get('uri')).text
                )

                # Initiate the download of the subtitle content
                console.log(f"[cyan]Downloading subtitle: [red]{sub_language.lower()}")
                futures.append(executor.submit(self.__save_subtitle_content, m3u8_sub_parser.subtitle[-1], sub_full_path))
            
            # Wait for all downloads to finish
            for future in futures:
                future.result()

    def __join_video__(self, vcodec = 'copy') -> str:
        """
        Join downloaded video segments into a single video file.

        Returns:
            str: Path of the joined video file.
        """

        path_join_video = os.path.join(self.base_path, "v_v.mp4")
        logging.info(f"JOIN video path: {path_join_video}")

        if not os.path.exists(path_join_video):

            # Join the video segments into a single video file
            join_video(
                video_path = self.downloaded_video[0].get('path'),
                out_path = path_join_video,
                vcodec = vcodec
            )

        print_duration_table(path_join_video)
        return path_join_video

    def __join_video_audio__(self) -> str:
        """
        Join downloaded video with audio segments into a single video file.

        Returns:
            str: Path of the joined video with audio file.
        """

        path_join_video_audio = os.path.join(self.base_path, "v_a.mp4")
        logging.info(f"JOIN audio path: {path_join_video_audio}")

        if not os.path.exists(path_join_video_audio):

            # Join the video with audio segments into a single video with audio file
            join_audios(
                video_path = self.downloaded_video[0].get('path'),
                audio_tracks = self.downloaded_audio,
                out_path = path_join_video_audio
            )

        print_duration_table(path_join_video_audio)
        return path_join_video_audio

    def __join_video_subtitles__(self, input_path: str) -> str:
        """
        Join downloaded video with subtitles.

        Args:
            - input_path (str): Path of the input video file.

        Returns:
            str: Path of the joined video with subtitles file.
        """

        path_join_video_subtitle = os.path.join(self.base_path, "v_s.mp4")
        logging.info(f"JOIN subtitle path: {path_join_video_subtitle}")

        if not os.path.exists(path_join_video_subtitle):

            # Join the video with subtitles
            join_subtitle(
                input_path,
                self.downloaded_subtitle,
                path_join_video_subtitle
            )

        print_duration_table(path_join_video_subtitle)
        return path_join_video_subtitle

    def __clean__(self, out_path: str) -> None:
        """
        Clean up temporary files and folders.

        Args:
            - out_path (str): Path of the output file.
        """

        # Check if file to rename exist
        logging.info(f"Check if end file converted exist: {out_path}")
        if out_path is None or not os.path.isfile(out_path):
            logging.error("Video file converted not exist.")
            sys.exit(0)

        # Rename the output file to the desired output filename if not exist
        if not os.path.exists(self.output_filename):

            # Rename file converted to original set in init
            os.rename(out_path, self.output_filename)

            # Print size of the file
            console.print(Panel(f"[bold green]Download completed![/bold green]\nFile size: [bold]{format_size(os.path.getsize(self.output_filename))}[/bold]", title=f"{os.path.basename(self.output_filename.replace('.mp4', ''))}", border_style="green"))

            # Delete all files except the output file
            delete_files_except_one(self.base_path, os.path.basename(self.output_filename))

            # Remove the base folder
            if REMOVE_SEGMENTS_FOLDER:
                remove_folder(self.base_path)

        else:
            logging.info("Video file converted already exist.")

    def start(self, server_ip: list = None) -> None:
        """
        Start the process of fetching, downloading, joining, and cleaning up the video.

        Args:
            - server_ip (list): A list of IP addresses to use in requests.
        """

        # Check if file already exist
        if os.path.exists(self.output_filename):
            self.m3u8_playlist = False
            self.m3u8_index = False
            console.log("[red]Output file already exist.")

        if self.m3u8_playlist:
            logging.info("Download from PLAYLIST")

            # Fetch the M3U8 playlist content
            if not len(str(self.m3u8_playlist).split("\n")) > 2:    # Is a single link
                m3u8_playlist_text = self.__df_make_req__(self.m3u8_playlist)

                # Add full URL of the M3U8 playlist to fix next .ts without https if necessary
                self.m3u8_url_fixer.set_playlist(self.m3u8_playlist) # !!!!!!!!!!!!!!!!!! to fix for playlist with text

            else:
                logging.warning("M3U8 master url not set.") # TO DO
                m3u8_playlist_text = self.m3u8_playlist

            # Save text playlist
            open(os.path.join(self.base_path, "tmp", "playlist.m3u8"), "w+").write(m3u8_playlist_text)


            # Collect information about the playlist
            self.__manage_playlist__(m3u8_playlist_text)

            # Start all download ...
            if DOWNLOAD_VIDEO:
                self.__donwload_video__(server_ip)
            if DOWNLOAD_AUDIO:
                self.__donwload_audio__(server_ip)
            if DOWNLOAD_SUB:
                self.__download_subtitle__()

            # Check file to convert
            converted_out_path = None
            there_is_video: bool = (len(self.downloaded_video) > 0)
            there_is_audio: bool = (len(self.downloaded_audio) > 0)
            there_is_subtitle: bool = (len(self.downloaded_subtitle) > 0)
            console.log(f"[cyan]Conversion [white]=> ([green]Audio: [yellow]{there_is_audio}[white], [green]Subtitle: [yellow]{there_is_subtitle}[white])")

            # Join audio and video
            if there_is_audio:
                converted_out_path = self.__join_video_audio__()

            # Join only video ( audio is present in the same ts files )
            else:
                if there_is_video:
                    converted_out_path = self.__join_video__()

            # Join subtitle
            if there_is_subtitle:
                if converted_out_path is not None:
                    converted_out_path = self.__join_video_subtitles__(converted_out_path)

            # Clean all tmp file
            self.__clean__(converted_out_path)


        elif self.m3u8_index:
            logging.info("Download from INDEX")

            # Add full URL of the M3U8 playlist to fix next .ts without https if necessary
            self.m3u8_url_fixer.set_playlist(self.m3u8_index)

            # Start all download ...
            self.__donwload_video__()

            # Convert video
            converted_out_path = self.__join_video__()

            # Clean all tmp file
            self.__clean__(converted_out_path)


        # Create download report
        if CREATE_REPORT:

            # Get variable to add
            current_date = datetime.today().date()
            base_filename = os.path.split(self.output_filename)[-1].replace('.mp4', '')
            filename_out_size = format_size(os.path.getsize(self.output_filename))

            # Add new row to table and save
            report_table.add_row_to_database(str(current_date), str(base_filename), str(filename_out_size))
            report_table.save_database()
