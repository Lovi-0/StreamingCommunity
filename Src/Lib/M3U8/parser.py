# 20.04.25

import logging


# Internal utilities
from .lib_parser import load


# External libraries
from Src.Lib.Request.my_requests import requests


# Costant
CODEC_MAPPINGS = {
    "video": {
        "avc1": "libx264",
        "avc2": "libx264",
        "avc3": "libx264",
        "avc4": "libx264",
        "hev1": "libx265",
        "hev2": "libx265",
        "hvc1": "libx265",
        "hvc2": "libx265",
        "vp8": "libvpx",
        "vp9": "libvpx-vp9",
        "vp10": "libvpx-vp9"
    },
    "audio": {
        "mp4a": "aac",
        "mp3": "libmp3lame",
        "ac-3": "ac3",
        "ec-3": "eac3",
        "opus": "libopus",
        "vorbis": "libvorbis"
    }
}
    
RESOLUTIONS = [
    (7680, 4320),
    (3840, 2160),
    (2560, 1440),
    (1920, 1080),
    (1280, 720),
    (640, 480)
]



class M3U8_Codec:
    """
    Represents codec information for an M3U8 playlist.
    """

    def __init__(self, bandwidth, resolution, codecs):
        """
        Initializes the M3U8Codec object with the provided parameters.

        Args:
            - bandwidth (int): Bandwidth of the codec.
            - resolution (str): Resolution of the codec.
            - codecs (str): Codecs information in the format "avc1.xxxxxx,mp4a.xx".
        """
        self.bandwidth = bandwidth
        self.resolution = resolution
        self.codecs = codecs
        self.audio_codec = None
        self.video_codec = None
        self.extract_codecs()
        self.parse_codecs()

    def extract_codecs(self):
        """
        Parses the codecs information to extract audio and video codecs.
        Extracted codecs are set as attributes: audio_codec and video_codec.
        """
        
        # Split the codecs string by comma
        codecs_list = self.codecs.split(',')

        # Separate audio and video codecs
        for codec in codecs_list:
            if codec.startswith('avc'):
                self.video_codec = codec
            elif codec.startswith('mp4a'):
                self.audio_codec = codec

    def convert_video_codec(self, video_codec_identifier) -> str:

        """
        Convert video codec identifier to codec name.

        Args:
            - video_codec_identifier (str): Identifier of the video codec.

        Returns:
            str: Codec name corresponding to the identifier.
        """

        # Extract codec type from the identifier
        codec_type = video_codec_identifier.split('.')[0]

        # Retrieve codec mapping from the provided mappings or fallback to static mappings
        video_codec_mapping = CODEC_MAPPINGS.get('video', {})
        codec_name = video_codec_mapping.get(codec_type)

        if codec_name:
            return codec_name
        
        else:
            logging.warning(f"No corresponding video codec found for {video_codec_identifier}. Using default codec libx264.")
            return "libx264"    # Default
        
    def convert_audio_codec(self, audio_codec_identifier) -> str:

        """
        Convert audio codec identifier to codec name.

        Args:
            - audio_codec_identifier (str): Identifier of the audio codec.

        Returns:
            str: Codec name corresponding to the identifier.
        """

        # Extract codec type from the identifier
        codec_type = audio_codec_identifier.split('.')[0]

        # Retrieve codec mapping from the provided mappings or fallback to static mappings
        audio_codec_mapping = CODEC_MAPPINGS.get('audio', {})
        codec_name = audio_codec_mapping.get(codec_type)

        if codec_name:
            return codec_name
        
        else:
            logging.warning(f"No corresponding audio codec found for {audio_codec_identifier}. Using default codec aac.")
            return "aac"        # Default
        
    def parse_codecs(self):
        """
        Parse video and audio codecs.
        This method updates `video_codec_name` and `audio_codec_name` attributes.
        """

        self.video_codec_name = self.convert_video_codec(self.video_codec)
        self.audio_codec_name = self.convert_audio_codec(self.audio_codec)

    def __str__(self):
        """
        Returns a string representation of the M3U8Codec object.
        """
        return f"BANDWIDTH={self.bandwidth},RESOLUTION={self.resolution},CODECS=\"{self.codecs}\""


class M3U8_Video:
    def __init__(self, video_playlist) -> None:
        """
        Initializes an M3U8_Video object with the provided video playlist.

        Args:
            - video_playlist (M3U8): An M3U8 object representing the video playlist.
        """
        self.video_playlist = video_playlist
    
    def get_best_uri(self):
        """
        Returns the URI with the highest resolution from the video playlist.

        Returns:
            tuple or None: A tuple containing the URI with the highest resolution and its resolution value, or None if the video list is empty.
        """
        if not self.video_playlist:
            return None
    
        best_uri = max(self.video_playlist, key=lambda x: x['resolution'])
        return best_uri['uri'], best_uri['resolution']

    def get_worst_uri(self):
        """
        Returns the URI with the lowest resolution from the video playlist.

        Returns:
            - tuple or None: A tuple containing the URI with the lowest resolution and its resolution value, or None if the video list is empty.
        """
        if not self.video_playlist:
            return None

        worst_uri = min(self.video_playlist, key=lambda x: x['resolution'])
        return worst_uri['uri'], worst_uri['resolution']

    def get_custom_uri(self, y_resolution):
        """
        Returns the URI corresponding to a custom resolution from the video list.

        Args:
            - video_list (list): A list of dictionaries containing video URIs and resolutions.
            - custom_resolution (tuple): A tuple representing the custom resolution.

        Returns:
            str or None: The URI corresponding to the custom resolution, or None if not found.
        """
        for video in self.video_playlist:
            logging.info(f"Check resolution from playlist: {int(video['resolution'][1])}, with input: {int(y_resolution)}")
            
            if int(video['resolution'][1]) == int(y_resolution):
                return video['uri'], video['resolution']
            
        return None, None
    
    def get_list_resolution(self):
        """
        Retrieve a list of resolutions from the video playlist.
        
        Returns:
            list: A list of resolutions extracted from the video playlist.
        """
        return [video['resolution'] for video in self.video_playlist]


class M3U8_Audio:
    def __init__(self, audio_playlist) -> None:
        """
        Initializes an M3U8_Audio object with the provided audio playlist.

        Args:
            - audio_playlist (M3U8): An M3U8 object representing the audio playlist.
        """  
        self.audio_playlist = audio_playlist

    def get_uri_by_language(self, language):
        """
        Returns a dictionary with 'name' and 'uri' given a specific language.

        Args:
            - audio_list (list): List of dictionaries containing audio information.
            - language (str): The desired language.

        Returns:
            dict or None: Dictionary with 'name', 'language', and 'uri' for the specified language, or None if not found.
        """
        for audio in self.audio_playlist:
            if audio['language'] == language:
                return {'name': audio['name'], 'language': audio['language'], 'uri': audio['uri']}
        return None

    def get_all_uris_and_names(self):
        """
        Returns a list of dictionaries containing all URIs and names.

        Args:
            - audio_list (list): List of dictionaries containing audio information.

        Returns:
            list: List of dictionaries containing 'name', 'language', and 'uri' for all audio in the list.
        """
        return [{'name': audio['name'], 'language': audio['language'], 'uri': audio['uri']} for audio in self.audio_playlist]

    def get_default_uri(self):
        """
        Returns the dictionary with 'default' equal to 'YES'.

        Args:
            - audio_list (list): List of dictionaries containing audio information.

        Returns:
            dict or None: Dictionary with 'default' equal to 'YES', or None if not found.
        """
        for audio in self.audio_playlist:
            if audio['default'] == 'YES':
                return audio.get('uri')
        return None


class M3U8_Subtitle:
    def __init__(self, subtitle_playlist) -> None:
        """
        Initializes an M3U8_Subtitle object with the provided subtitle playlist.

        Args:
            - subtitle_playlist (M3U8): An M3U8 object representing the subtitle playlist.
        """
        self.subtitle_playlist = subtitle_playlist

    def get_uri_by_language(self, language):
        """
        Returns a dictionary with 'name' and 'uri' given a specific language for subtitles.

        Args:
            - subtitle_list (list): List of dictionaries containing subtitle information.
            - language (str): The desired language.

        Returns:
            dict or None: Dictionary with 'name' and 'uri' for the specified language for subtitles, or None if not found.
        """
        for subtitle in self.subtitle_playlist:
            if subtitle['language'] == language:
                return {'name': subtitle['name'], 'uri': subtitle['uri']}
        return None

    def get_all_uris_and_names(self):
        """
        Returns a list of dictionaries containing all URIs and names of subtitles.

        Args:
            - subtitle_list (list): List of dictionaries containing subtitle information.

        Returns:
            list: List of dictionaries containing 'name' and 'uri' for all subtitles in the list.
        """
        return [{'name': subtitle['name'], 'language': subtitle['language'], 'uri': subtitle['uri']} for subtitle in self.subtitle_playlist]

    def get_default_uri(self):
        """
        Returns the dictionary with 'default' equal to 'YES' for subtitles.

        Args:
            - subtitle_list (list): List of dictionaries containing subtitle information.

        Returns:
            dict or None: Dictionary with 'default' equal to 'YES' for subtitles, or None if not found.
        """
        for subtitle in self.subtitle_playlist:
            if subtitle['default'] == 'YES':
                return subtitle
        return None

    def download_all(self, custom_subtitle):
        """
        Download all subtitles listed in the object's attributes, filtering based on a provided list of custom subtitles.

        Args:
            - custom_subtitle (list): A list of custom subtitles to download.

        Returns:
            list: A list containing dictionaries with subtitle information including name, language, and URI.
        """
            
        output = []  # Initialize an empty list to store subtitle information

        # Iterate through all available subtitles
        for obj_subtitle in self.subtitle_get_all_uris_and_names():

            # Check if the subtitle name is not in the list of custom subtitles, and skip if not found
            if obj_subtitle.get('name') not in custom_subtitle:
                continue

            # Send a request to retrieve the subtitle content
            logging.info(f"Download subtitle: {obj_subtitle.get('name')}")
            response_subitle = requests.get(obj_subtitle.get('uri'))

            try:
                # Try to extract the VTT URL from the subtitle content
                sub_parse = M3U8_Parser()
                sub_parse.parse_data(obj_subtitle.get('uri'), response_subitle.text)
                url_subititle = sub_parse.subtitle[0]

                output.append({
                    'name': obj_subtitle.get('name'),
                    'language': obj_subtitle.get('language'),
                    'uri': url_subititle
                })

            except Exception as e:
                logging.error(f"Cant donwload: {obj_subtitle.get('name')}, error: {e}")

        return output


class M3U8_Parser:
    def __init__(self):
        self.segments = []
        self.video_playlist = []
        self.keys = None
        self.subtitle_playlist = []
        self.subtitle = []
        self.audio_playlist = []
        self.codec: M3U8_Codec = None
        self._video: M3U8_Video = None
        self._audio: M3U8_Audio = None
        self._subtitle: M3U8_Subtitle = None

        self.__create_variable__()

    def parse_data(self, uri, raw_content) -> None:
        """
        Extracts all information present in the provided M3U8 content.

        Args:
            - m3u8_content (str): The content of the M3U8 file.
        """


        # Get obj of the m3u8 text content download, dictionary with video, audio, segments, subtitles
        m3u8_obj = load(raw_content, uri)

        self.__parse_video_info__(m3u8_obj)
        self.__parse_encryption_keys__(m3u8_obj)
        self.__parse_subtitles_and_audio__(m3u8_obj)
        self.__parse_segments__(m3u8_obj)

    @staticmethod
    def extract_resolution(uri: str) -> int:
        """
        Extracts the video resolution from the given URI.

        Args:
            - uri (str): The URI containing video information.

        Returns:
            int: The video resolution if found, otherwise 0.
        """

        # Log
        logging.info(f"Try extract resolution from: {uri}")

        for resolution in RESOLUTIONS:
            if "http" in str(uri):
                if str(resolution[1]) in uri:
                    return resolution
            
        # Default resolution return (not best)
        logging.error("No resolution found with custom parsing.")
        logging.warning("Try set remove duplicate line to TRUE.")
        return (0, 0)

    def __parse_video_info__(self, m3u8_obj) -> None:
        """
        Extracts video information from the M3U8 object.

        Args:
            - m3u8_obj: The M3U8 object containing video playlists.
        """

        try:
            for playlist in m3u8_obj.playlists:

                # Direct access resolutions in m3u8 obj
                if playlist.stream_info.resolution is not None:

                    self.video_playlist.append({
                        "uri": playlist.uri, 
                        "resolution": playlist.stream_info.resolution
                    })
                
                # Find resolutions in uri
                else:

                    self.video_playlist.append({
                        "uri": playlist.uri, 
                        "resolution": M3U8_Parser.extract_resolution(playlist.uri)
                    })    

                    # Dont stop
                    continue

                # Check if all key is present to create codec
                try:
                    self.codec = M3U8_Codec(
                        playlist.stream_info.bandwidth,
                        playlist.stream_info.resolution,
                        playlist.stream_info.codecs
                    )
                except:
                    logging.error(f"Error parsing codec: {e}")

        except Exception as e:
            logging.error(f"Error parsing video info: {e}")

    def __parse_encryption_keys__(self, m3u8_obj) -> None:
        """
        Extracts encryption keys from the M3U8 object.

        Args:
            - m3u8_obj: The M3U8 object containing encryption keys.
        """
        try:

            if m3u8_obj.key is not None:
                if self.keys is None:
                    self.keys = {
                        'method': m3u8_obj.key.method,
                        'iv': m3u8_obj.key.iv,
                        'uri': m3u8_obj.key.uri
                    }


        except Exception as e:
            logging.error(f"Error parsing encryption keys: {e}")
            pass

    def __parse_subtitles_and_audio__(self, m3u8_obj) -> None:
        """
        Extracts subtitles and audio information from the M3U8 object.

        Args:
            - m3u8_obj: The M3U8 object containing subtitles and audio data.
        """
        try:
            for media in m3u8_obj.media:
                if media.type == "SUBTITLES":
                    self.subtitle_playlist.append({
                        "type": media.type,
                        "name": media.name,
                        "default": media.default,
                        "language": media.language,
                        "uri": media.uri
                    })

                if media.type == "AUDIO":
                    self.audio_playlist.append({
                        "type": media.type,
                        "name": media.name,
                        "default": media.default,
                        "language": media.language,
                        "uri": media.uri
                    })

        except Exception as e:
            logging.error(f"Error parsing subtitles and audio: {e}")

    def __parse_segments__(self, m3u8_obj) -> None:
        """
        Extracts segment information from the M3U8 object.

        Args:
            - m3u8_obj: The M3U8 object containing segment data.
        """

        try:
            for segment in m3u8_obj.segments:
                if "vtt" not in segment.uri:
                    self.segments.append(segment.uri)
                else:
                    self.subtitle.append(segment.uri)

        except Exception as e:
            logging.error(f"Error parsing segments: {e}")

    def __create_variable__(self):
        """
        Initialize variables for video, audio, and subtitle playlists.
        """

        self._video = M3U8_Video(self.video_playlist)
        self._audio = M3U8_Audio(self.audio_playlist)
        self._subtitle = M3U8_Subtitle(self.subtitle_playlist)
