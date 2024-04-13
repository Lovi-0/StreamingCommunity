# 29.04.25

import logging


# Internal utilities
from Src.Util.headers import get_headers


# External libraries
import requests
from m3u8 import M3U8


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


def extract_resolution(uri: str) -> int:
    """
    Extracts the video resolution from the given URI.

    Args:
    - uri (str): The URI containing video information.

    Returns:
    - int: The video resolution if found, otherwise 0.
    """

    for resolution in RESOLUTIONS:
        if str(resolution[1]) in uri:
            return resolution
        
    # Default resolution return (not best)
    logging.error("No resolution find with custom parsing.")
    return -1


class M3U8_Codec():
    """
    Represents codec information for an M3U8 playlist.

    Attributes:
    - bandwidth (int): Bandwidth of the codec.
    - resolution (str): Resolution of the codec.
    - codecs (str): Codecs information in the format "avc1.xxxxxx,mp4a.xx".
    - audio_codec (str): Audio codec extracted from the codecs information.
    - video_codec (str): Video codec extracted from the codecs information.
    """

    def __init__(self, bandwidth, resolution, codecs):
        """
        Initializes the M3U8Codec object with the provided parameters.

        Parameters:
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

        Parameters:
        - video_codec_identifier (str): Identifier of the video codec.

        Returns:
        - str: Codec name corresponding to the identifier.
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

        Parameters:
        - audio_codec_identifier (str): Identifier of the audio codec.

        Returns:
        - str: Codec name corresponding to the identifier.
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
        logging.info(f"CODECS={self.video_codec_name},{self.audio_codec_name}")

    def __str__(self):
        """
        Returns a string representation of the M3U8Codec object.
        """
        return f"BANDWIDTH={self.bandwidth},RESOLUTION={self.resolution},CODECS=\"{self.codecs}\""


class M3U8_Parser:
    def __init__(self, DOWNLOAD_SPECIFIC_SUBTITLE = None):
        """
        Initializes M3U8_Parser with empty lists for segments, playlists, keys, and subtitles.
        """

        self.segments = []
        self.video_playlist = []
        self.keys = {}
        self.subtitle_playlist = []     # No vvt ma url a vvt
        self.subtitle = []              # Url a vvt
        self.audio_ts = []
        self.codec: M3U8_Codec = None
        self.DOWNLOAD_SPECIFIC_SUBTITLE = DOWNLOAD_SPECIFIC_SUBTITLE

    def parse_data(self, m3u8_content: str) -> None:
        """
        Extracts all information present in the provided M3U8 content.

        Args:
        - m3u8_content (str): The content of the M3U8 file.
        """
        try:
            # Basic input validation
            if not m3u8_content.strip():
                logging.error("M3U8 content is empty or whitespace.")
                return

            # Get obj of the m3u8 text content download, dictionary with video, audio, segments, subtitles
            m3u8_obj = M3U8(m3u8_content)

            self.parse_video_info(m3u8_obj)
            self.parse_encryption_keys(m3u8_obj)
            self.parse_subtitles_and_audio(m3u8_obj)
            self.parse_segments(m3u8_obj)

        except Exception as e:
            logging.error(f"Error parsing M3U8 content: {e}")

    def parse_video_info(self, m3u8_obj) -> None:
        """
        Extracts video information from the M3U8 object.

        Args:
        - m3u8_obj: The M3U8 object containing video playlists.
        """

        try:
            for playlist in m3u8_obj.playlists:

                # Direct access resolutions in m3u8 obj
                try:
                    self.video_playlist.append({
                        "uri": playlist.uri, 
                        "width": playlist.stream_info.get('resolution')
                    })

                # Find resolutions in uri
                except:
                    self.video_playlist.append({
                        "uri": playlist.uri, 
                        "width": extract_resolution(playlist.uri)
                    })    

                    # Dont stop
                    continue


                # Check if all key is present to create codec
                if all(key in playlist.stream_info for key in ('bandwidth', 'resolution', 'codecs')):
                    self.codec = M3U8_Codec(
                        playlist.stream_info.get('bandwidth'),
                        playlist.stream_info.get('resolution'),
                        playlist.stream_info.get('codecs')
                    )

                # if not we cant create codec
                else:
                    self.codec = None

                logging.info(f"Parse: {playlist.stream_info}")
                if self.codec:
                    logging.info(f"Coded test: {self.codec.bandwidth}")

        except Exception as e:
            logging.error(f"Error parsing video info: {e}")

    def parse_encryption_keys(self, m3u8_obj) -> None:
        """
        Extracts encryption keys from the M3U8 object.

        Args:
        - m3u8_obj: The M3U8 object containing encryption keys.
        """
        try:
            for key in m3u8_obj.keys:
                if key is not None:
                    self.keys = {
                        "method": key.method,
                        "uri": key.uri,
                        "iv": key.iv
                    }

        except Exception as e:
            logging.error(f"Error parsing encryption keys: {e}")

    def parse_subtitles_and_audio(self, m3u8_obj) -> None:
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
                    self.audio_ts.append({
                        "type": media.type,
                        "name": media.name,
                        "default": media.default,
                        "language": media.language,
                        "uri": media.uri
                    })

        except Exception as e:
            logging.error(f"Error parsing subtitles and audio: {e}")

    def parse_segments(self, m3u8_obj) -> None:
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

    def get_resolution(self, uri: str) -> (int):
        """
        Gets the resolution from the provided URI.

        Args:
        - uri (str): The URI to extract resolution from.

        Returns:
        - int: The resolution if found, otherwise 0.
        """

        if '1080' in uri:
            return 1080
        elif '720' in uri:
            return 720
        elif '480' in uri:
            return 480
        else:
            return 0

    def get_best_quality(self) -> (dict):
        """
        Returns the URI of the M3U8 playlist with the best quality.

        Returns:
        - str: The URI of the M3U8 playlist with the best quality and decoding if present, otherwise return None
        """

        if self.video_playlist:

            try:

                # Sort the list of video playlist items based on the 'width' attribute in descending order.
                # The 'width' attribute is extracted using the lambda function as the sorting key.
                sorted_uris = sorted(self.video_playlist, key=lambda x: x['width'], reverse=True)

                # And get the first with best resolution
                return sorted_uris[0]
            
            except:
                logging.error("Error: Can't find M3U8 resolution by width...")
                logging.info("Try searching in URI")

                # Sort the list of video playlist items based on the 'width' attribute if present,
                # otherwise, use the resolution obtained from the 'uri' attribute as a fallback.
                # Sorting is done in descending order (reverse=True).
                sorted_uris = sorted(self.video_playlist, key=lambda x: x.get('width') if x.get('width') is not None else self.get_resolution(x.get('uri')), reverse=True)

                # And get the first with best resolution
                return sorted_uris[0]
        else:

            logging.info("No video playlists found.")
            return None
        
    def get_subtitles(self):
        """
        Download all subtitles if present.

        Return:
        - list: list of subtitle with [name_language, uri] or None if there is no subtitle
        """

        # Create full path where store data of subtitle
        logging.info("Download subtitle ...")

        if self.subtitle_playlist:
            output = []

            # For all subtitle find
            for sub_info in self.subtitle_playlist:

                # Get language name
                name_language = sub_info.get("language")
                logging.info(f"Find subtitle: {name_language}")

                # Check if there is custom subtitles to download
                if len(self.DOWNLOAD_SPECIFIC_SUBTITLE) > 0:
                    
                    # Check if language in list
                    if name_language not in self.DOWNLOAD_SPECIFIC_SUBTITLE:
                        continue

                # Make request to m3u8 subtitle to extract vtt
                logging.info(f"Download subtitle: {name_language}")
                req_sub_content = requests.get(sub_info.get("uri"), headers={'user-agent': get_headers()})

                try:

                    # Try extract vtt url
                    sub_parse = M3U8_Parser()
                    sub_parse.parse_data(req_sub_content.text)
                    url_subititle = sub_parse.subtitle[0]

                    # Add name and url to output list
                    output.append({
                        'name': sub_info.get('name'),
                        'language': name_language, 
                        'uri': url_subititle
                    })

                except Exception as e:
                    logging.error(f"Cant donwload: {name_language}, error: {e}")

            # Return
            return output

        else:
            logging.info("No subtitle find")
            return None

    def get_track_audios(self) -> list:
        """
        Return a list of available audio files with dictionaries {'language': xx, 'uri: xx}

        Returns:
            list: A list of dictionaries containing language and URI information for audio tracks, or None if no audio tracks are found.
        """

        logging.info(f"Finding {len(self.audio_ts)} playlist(s) with audio.")

        if self.audio_ts:
            logging.info("Getting list of available audio names")
            list_output = []

            # For all languages present in m3u8
            for obj_audio in self.audio_ts:

                # Add language and URI
                list_output.append({
                    'language': obj_audio.get('language'),
                    'uri': obj_audio.get('uri')
                })

            # Return
            return list_output

        else:
            logging.info("No audio tracks found")
            return None

    def get_default_subtitle(self):
        """
        Retrieves the default subtitle information from the subtitle playlist.

        Returns:
            dict: A dictionary containing the name and URI of the default subtitle, or None if no default subtitle is found.
        """

        dict_default_sub = None

        # Check if there are subtitles in the playlist
        if self.subtitle_playlist:

            # Iterate through each subtitle in the playlist
            for sub_info in self.subtitle_playlist:

                # Check if the subtitle is marked as default
                is_default = sub_info.get("default")

                if is_default == "YES":
                    dict_default_sub = {
                        'name': sub_info.get('name'),
                        'uri': sub_info.get('uri'),
                    }

        # Return the default subtitle dictionary
        return dict_default_sub
    
    def get_default_track_audio(self):
        """
        Retrieves the default audio track information from the audio_ts list.

        Returns:
            dict: A dictionary containing the name and URI of the default audio track, or None if no default audio track is found.
        """

        dict_default_audio = None

        # Check if there are audio tracks in the list
        if self.audio_ts:

            # Iterate through each audio track object in the list
            for obj_audio in self.audio_ts:

                # Check if the audio track is marked as default
                is_default = obj_audio.get("default")

                if is_default == "YES":
                    dict_default_audio = {
                        'name': obj_audio.get('name'),
                        'uri': obj_audio.get('uri'),
                    }

        # Return the default audio track dictionary
        return dict_default_audio
    