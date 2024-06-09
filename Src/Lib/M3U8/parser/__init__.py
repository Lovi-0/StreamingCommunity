# 15.04.24

import os


# Internal utilities
from .model import M3U8


def load(raw_content, uri):
    """
    Parses the content of an M3U8 playlist and returns an M3U8 object.

    Args:
        raw_content (str): The content of the M3U8 playlist as a string.
        uri (str): The URI of the M3U8 playlist file or stream.

    Returns:
        M3U8: An object representing the parsed M3U8 playlist.

    Raises:
        IOError: If the raw_content is empty or if the URI cannot be accessed.
        ValueError: If the raw_content is not a valid M3U8 playlist format.

    Example:
        >>> m3u8_content = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n#EXT-X-MEDIA-SEQUENCE:0\n#EXTINF:10.0,\nhttp://example.com/segment0.ts\n#EXTINF:10.0,\nhttp://example.com/segment1.ts\n"
        >>> uri = "http://example.com/playlist.m3u8"
        >>> playlist = load(m3u8_content, uri)
    """

    if not raw_content:
        raise IOError("Empty content provided.")

    if not uri:
        raise IOError("Empty URI provided.")

    base_uri = os.path.dirname(uri)
    return M3U8(raw_content, base_uri=base_uri)