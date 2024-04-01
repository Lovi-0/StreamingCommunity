# 29.04.25

# Class import
from Src.Util.headers import get_headers

# Import
from m3u8 import M3U8
import logging
import requests

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
        self.DOWNLOAD_SPECIFIC_SUBTITLE = DOWNLOAD_SPECIFIC_SUBTITLE

    def parse_data(self, m3u8_content: str) -> (None):
        """
        Extracts all information present in the provided M3U8 content.

        Args:
        - m3u8_content (str): The content of the M3U8 file.
        """

        try:

            # Get obj of the m3u8 text content download, dictionary with video, audio, segments, subtitles
            m3u8_obj = M3U8(m3u8_content)

            # Collect video info with url, resolution and codecs
            for playlist in m3u8_obj.playlists:
                self.video_playlist.append({
                    "uri": playlist.uri, 
                    "width": playlist.stream_info.resolution, 
                    "codecs": playlist.stream_info.codecs
            })

            # Collect info of encryption if present, method, uri and iv
            for key in m3u8_obj.keys:
                if key is not None:
                    self.keys = ({
                        "method": key.method,
                        "uri": key.uri,
                        "iv": key.iv
                    })

            # Collect info of subtitles, type, name, language and uri
            # for audio and subtitles
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

            # Collect info about url of subtitles or segmenets
            # m3u8 playlist
            # m3u8 index
            for segment in m3u8_obj.segments:

                # Collect uri of request to vtt
                if "vtt" not in segment.uri:
                    self.segments.append(segment.uri)

                # Collect info of subtitle 
                else:
                    self.subtitle.append(segment.uri)

        except Exception as e:
            logging.error(f"[M3U8_Parser] Error parsing M3U8 content: {e}")

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
                logging.error("[M3U8_Parser] Error: Can't find M3U8 resolution by width...")
                logging.info("[M3U8_Parser] Try searching in URI")

                # Sort the list of video playlist items based on the 'width' attribute if present,
                # otherwise, use the resolution obtained from the 'uri' attribute as a fallback.
                # Sorting is done in descending order (reverse=True).
                sorted_uris = sorted(self.video_playlist, key=lambda x: x.get('width') if x.get('width') is not None else self.get_resolution(x.get('uri')), reverse=True)

                # And get the first with best resolution
                return sorted_uris[0]
        else:

            logging.info("[M3U8_Parser] No video playlists found.")
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
                logging.info(f"[M3U8_Parser] Find subtitle: {name_language}")

                # Check if there is custom subtitles to download
                if len(self.DOWNLOAD_SPECIFIC_SUBTITLE) > 0:
                    
                    # Check if language in list
                    if name_language not in self.DOWNLOAD_SPECIFIC_SUBTITLE:
                        continue

                # Make request to m3u8 subtitle to extract vtt
                logging.info(f"[M3U8_Parser] Download subtitle: {name_language}")
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
                    logging.error(f"[M3U8_Parser] Cant donwload: {name_language}, error: {e}")

            # Return
            return output

        else:
            logging.info("[M3U8_Parser] No subtitle find")
            return None

    def get_track_audios(self) -> list:
        """
        Return a list of available audio files with dictionaries {'language': xx, 'uri: xx}

        Returns:
            list: A list of dictionaries containing language and URI information for audio tracks, or None if no audio tracks are found.
        """

        logging.info(f"[M3U8_Parser] Finding {len(self.audio_ts)} playlist(s) with audio.")

        if self.audio_ts:
            logging.info("[M3U8_Parser] Getting list of available audio names")
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
            logging.info("[M3U8_Parser] No audio tracks found")
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