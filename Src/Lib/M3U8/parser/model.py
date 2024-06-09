# 15.04.24

import os
from collections import namedtuple


# Internal utilities
from ..parser import parser


# Variable
StreamInfo = namedtuple('StreamInfo', ['bandwidth', 'program_id', 'resolution', 'codecs'])
Media = namedtuple('Media', ['uri', 'type', 'group_id', 'language', 'name','default', 'autoselect', 'forced', 'characteristics'])


class M3U8:
    """
    Represents a single M3U8 playlist. Should be instantiated with the content as string.

    Args:
        - content: the m3u8 content as string
        - base_path: all urls (key and segments url) will be updated with this base_path,
            ex: base_path = "http://videoserver.com/hls"
        - base_uri: uri the playlist comes from. it is propagated to SegmentList and Key
            ex: http://example.com/path/to

    Attribute:
        - key: it's a `Key` object, the EXT-X-KEY from m3u8. Or None
        - segments: a `SegmentList` object, represents the list of `Segment`s from this playlist
        - is_variant: Returns true if this M3U8 is a variant playlist, with links to other M3U8s with different bitrates.
            If true, `playlists` is a list of the playlists available, and `iframe_playlists` is a list of the i-frame playlists available.
        - is_endlist: Returns true if EXT-X-ENDLIST tag present in M3U8.
            Info: http://tools.ietf.org/html/draft-pantos-http-live-streaming-07#section-3.3.8
        - playlists: If this is a variant playlist (`is_variant` is True), returns a list of Playlist objects
        - iframe_playlists: If this is a variant playlist (`is_variant` is True), returns a list of IFramePlaylist objects
        - playlist_type: A lower-case string representing the type of the playlist, which can be one of VOD (video on demand) or EVENT.
        - media: If this is a variant playlist (`is_variant` is True), returns a list of Media objects
        - target_duration: Returns the EXT-X-TARGETDURATION as an integer
            Info: http://tools.ietf.org/html/draft-pantos-http-live-streaming-07#section-3.3.2
        - media_sequence: Returns the EXT-X-MEDIA-SEQUENCE as an integer
            Info: http://tools.ietf.org/html/draft-pantos-http-live-streaming-07#section-3.3.3
        - program_date_time: Returns the EXT-X-PROGRAM-DATE-TIME as a string
            Info: http://tools.ietf.org/html/draft-pantos-http-live-streaming-07#section-3.3.5
        - version: Return the EXT-X-VERSION as is
        - allow_cache: Return the EXT-X-ALLOW-CACHE as is
        - files: Returns an iterable with all files from playlist, in order. This includes segments and key uri, if present.
        - base_uri: It is a property (getter and setter) used by SegmentList and Key to have absolute URIs.
        - is_i_frames_only: Returns true if EXT-X-I-FRAMES-ONLY tag present in M3U8.
            Guide: http://tools.ietf.org/html/draft-pantos-http-live-streaming-07#section-3.3.12

    """

    # Mapping of simple attributes (obj attribute, parser attribute)
    SIMPLE_ATTRIBUTES = (
        ('is_variant',       'is_variant'),
        ('is_endlist',       'is_endlist'),
        ('is_i_frames_only', 'is_i_frames_only'),
        ('target_duration',  'targetduration'),
        ('media_sequence',   'media_sequence'),
        ('program_date_time',   'program_date_time'),
        ('version',          'version'),
        ('allow_cache',      'allow_cache'),
        ('playlist_type',    'playlist_type')
    )

    def __init__(self, content=None, base_path=None, base_uri=None):
        """
        Initialize the M3U8 object.

        Parameters:
        - content: M3U8 content (string).
        - base_path: Base path for relative URIs (string).
        - base_uri: Base URI for absolute URIs (string).
        """
        if content is not None:
            self.data = parser.parse(content)
        else:
            self.data = {}
        self._base_uri = base_uri
        self.base_path = base_path
        self._initialize_attributes()

    def _initialize_attributes(self):
        """
        Initialize attributes based on parsed data.
        """
        # Initialize key and segments
        self.key = Key(base_uri=self.base_uri, **self.data.get('key', {})) if 'key' in self.data else None
        self.segments = SegmentList([Segment(base_uri=self.base_uri, **params) for params in self.data.get('segments', [])])

        # Initialize simple attributes
        for attr, param in self.SIMPLE_ATTRIBUTES:
            setattr(self, attr, self.data.get(param))

        # Initialize files, media, playlists, and iframe_playlists
        self.files = []
        if self.key:
            self.files.append(self.key.uri)
        self.files.extend(self.segments.uri)

        self.media = [Media(
            uri = media.get('uri'), 
            type = media.get('type'), 
            group_id = media.get('group_id'),
            language = media.get('language'), 
            name = media.get('name'), 
            default = media.get('default'),
            autoselect = media.get('autoselect'), 
            forced = media.get('forced'),
            characteristics = media.get('characteristics')) 
            for media in self.data.get('media', [])
        ]
        self.playlists = PlaylistList([Playlist(
                base_uri = self.base_uri, 
                media = self.media, 
                **playlist
            )for playlist in self.data.get('playlists', [])
        ])
        self.iframe_playlists = PlaylistList()
        for ifr_pl in self.data.get('iframe_playlists', []):
            self.iframe_playlists.append(
                IFramePlaylist(
                    base_uri = self.base_uri, 
                    uri = ifr_pl['uri'],
                    iframe_stream_info=ifr_pl['iframe_stream_info'])
            )

    @property
    def base_uri(self):
        """
        Get the base URI.
        """
        return self._base_uri

    @base_uri.setter
    def base_uri(self, new_base_uri):
        """
        Set the base URI.
        """
        self._base_uri = new_base_uri
        self.segments.base_uri = new_base_uri


class BasePathMixin:
    """
    Mixin class for managing base paths.
    """
    @property
    def base_path(self):
        """
        Get the base path.
        """
        return os.path.dirname(self.uri)

    @base_path.setter
    def base_path(self, newbase_path):
        """
        Set the base path.
        """
        if not self.base_path:
            self.uri = "%s/%s" % (newbase_path, self.uri)
        self.uri = self.uri.replace(self.base_path, newbase_path)


class GroupedBasePathMixin:
    """
    Mixin class for managing base paths across a group of items.
    """

    def _set_base_uri(self, new_base_uri):
        """
        Set the base URI for each item in the group.
        """
        for item in self:
            item.base_uri = new_base_uri

    base_uri = property(None, _set_base_uri)

    def _set_base_path(self, new_base_path):
        """
        Set the base path for each item in the group.
        """
        for item in self:
            item.base_path = new_base_path

    base_path = property(None, _set_base_path)


class Segment(BasePathMixin):
    """
    Class representing a segment in an M3U8 playlist.
    Inherits from BasePathMixin for managing base paths.
    """

    def __init__(self, uri, base_uri, program_date_time=None, duration=None,
                 title=None, byterange=None, discontinuity=False, key=None):
        """
        Initialize a Segment object.

        Args:
            - uri: URI of the segment.
            - base_uri: Base URI for the segment.
            - program_date_time: Returns the EXT-X-PROGRAM-DATE-TIME as a datetime
                Guide: http://tools.ietf.org/html/draft-pantos-http-live-streaming-07#section-3.3.5
            - duration: Duration of the segment (optional).
            - title: Title attribute from EXTINF parameter
            - byterange: Byterange information of the segment (optional).
            - discontinuity: Returns a boolean indicating if a EXT-X-DISCONTINUITY tag exists
                Guide: http://tools.ietf.org/html/draft-pantos-http-live-streaming-13#section-3.4.11
            - key: Key for encryption (optional).
        """
        self.uri = uri
        self.duration = duration
        self.title = title
        self.base_uri = base_uri
        self.byterange = byterange
        self.program_date_time = program_date_time
        self.discontinuity = discontinuity
        #self.key = key


class SegmentList(list, GroupedBasePathMixin):
    """
    Class representing a list of segments in an M3U8 playlist.
    Inherits from list and GroupedBasePathMixin for managing base paths across a group of items.
    """

    @property
    def uri(self):
        """
        Get the URI of each segment in the SegmentList.

        Returns:
        - List of URIs of segments in the SegmentList.
        """
        return [seg.uri for seg in self]


class Key(BasePathMixin):
    """
    Class representing a key used for encryption in an M3U8 playlist.
    Inherits from BasePathMixin for managing base paths.
    """

    def __init__(self, method, uri, base_uri, iv=None):
        """
        Initialize a Key object.

        Args:
            - method: Encryption method. 
                ex: "AES-128"
            - uri: URI of the key.
                ex: "https://priv.example.com/key.php?r=52"
            - base_uri: Base URI for the key.
                ex: http://example.com/path/to
            - iv: Initialization vector (optional).
                ex: 0X12A
        """
        self.method = method
        self.uri = uri
        self.iv = iv
        self.base_uri = base_uri


class Playlist(BasePathMixin):
    """
    Playlist object representing a link to a variant M3U8 with a specific bitrate.

    More info: http://tools.ietf.org/html/draft-pantos-http-live-streaming-07#section-3.3.10
    """

    def __init__(self, uri, stream_info, media, base_uri):
        """
        Initialize a Playlist object.

        Args:
            - uri: URI of the playlist.
            - stream_info: is a named tuple containing the attributes: `program_id`,
            - media: List of Media objects associated with the playlist.
            - base_uri: Base URI for the playlist.
        """
        self.uri = uri
        self.base_uri = base_uri

        # Extract resolution information from stream_info
        resolution = stream_info.get('resolution')
        if resolution is not None:
            values = resolution.split('x')
            resolution_pair = (int(values[0]), int(values[1]))
        else:
            resolution_pair = None

        # Create StreamInfo object
        self.stream_info = StreamInfo(
            bandwidth = stream_info['bandwidth'],
            program_id = stream_info.get('program_id'),
            resolution = resolution_pair,
            codecs = stream_info.get('codecs')
        )

        # Filter media based on group ID and media type
        self.media = []
        for media_type in ('audio', 'video', 'subtitles'):
            group_id = stream_info.get(media_type)
            if group_id:
                self.media += filter(lambda m: m.group_id == group_id, media)


class IFramePlaylist(BasePathMixin):
    """
    Class representing an I-Frame playlist in an M3U8 playlist.
    Inherits from BasePathMixin for managing base paths.
    """

    def __init__(self, base_uri, uri, iframe_stream_info):
        """
        Initialize an IFramePlaylist object.

        Args:
            - base_uri: Base URI for the I-Frame playlist.
            - uri: URI of the I-Frame playlist.
            - iframe_stream_info, is a named tuple containing the attributes: 
                `program_id`, `bandwidth`, `codecs` and `resolution` which is a tuple (w, h) of integers
        """
        self.uri = uri
        self.base_uri = base_uri

        # Extract resolution information from iframe_stream_info
        resolution = iframe_stream_info.get('resolution')
        if resolution is not None:
            values = resolution.split('x')
            resolution_pair = (int(values[0]), int(values[1]))
        else:
            resolution_pair = None

        # Create StreamInfo object for I-Frame playlist
        self.iframe_stream_info = StreamInfo(
            bandwidth = iframe_stream_info.get('bandwidth'),
            program_id = iframe_stream_info.get('program_id'),
            resolution = resolution_pair,
            codecs = iframe_stream_info.get('codecs')
        )

class PlaylistList(list, GroupedBasePathMixin):
    """
    Class representing a list of playlists in an M3U8 playlist.
    Inherits from list and GroupedBasePathMixin for managing base paths across a group of items.
    """

    def __str__(self):
        """
        Return a string representation of the PlaylistList.

        Returns:
        - String representation of the PlaylistList.
        """
        output = [str(playlist) for playlist in self]
        return '\n'.join(output)
