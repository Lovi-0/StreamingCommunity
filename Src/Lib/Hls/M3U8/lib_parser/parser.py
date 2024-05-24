# 15.04.24

import re
import logging
import datetime


# Internal utilities
from ..lib_parser import protocol
from ._util import (
    remove_quotes,
    remove_quotes_parser,
    normalize_attribute
)


# External utilities
from Src.Util._jsonConfig import config_manager


# Variable
REMOVE_EMPTY_ROW = config_manager.get_bool('M3U8_PARSER', 'skip_empty_row_playlist')
ATTRIBUTELISTPATTERN = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')


def parse(content):
    """
    Given an M3U8 playlist content, parses the content and extracts metadata.

    Args:
        content (str): The M3U8 playlist content.

    Returns:
        dict: A dictionary containing the parsed metadata.
    """

    # Initialize data dictionary with default values
    data = {
        'is_variant': False,
        'is_endlist': False,
        'is_i_frames_only': False,
        'playlist_type': None,
        'playlists': [],
        'iframe_playlists': [],
        'segments': [],
        'media': [],
    }

    # Initialize state dictionary for tracking parsing state
    state = {
        'expect_segment': False,
        'expect_playlist': False,
    }

    # Iterate over lines in the content
    content = content.split("\n")
    content_length = len(content)
    i = 0

    while i < content_length:
        line = content[i]
        line_stripped = line.strip()
        is_end = i + 1 == content_length - 2

        if REMOVE_EMPTY_ROW:
            if i < content_length - 2:
                actual_row = extract_params(line_stripped)
                next_row = extract_params(content[i + 2].strip())

                if actual_row is not None and next_row is None and not is_end:
                    logging.info(f"Skip row: {line_stripped}")
                    i += 1
                    continue

        i += 1

        if line.startswith(protocol.ext_x_byterange):
            _parse_byterange(line, state)
            state['expect_segment'] = True

        elif state['expect_segment']:
            _parse_ts_chunk(line, data, state)
            state['expect_segment'] = False

        elif state['expect_playlist']:
            _parse_variant_playlist(line, data, state)
            state['expect_playlist'] = False

        elif line.startswith(protocol.ext_x_targetduration):
            _parse_simple_parameter(line, data, float)
        elif line.startswith(protocol.ext_x_media_sequence):
            _parse_simple_parameter(line, data, int)
        elif line.startswith(protocol.ext_x_discontinuity):
            state['discontinuity'] = True
        elif line.startswith(protocol.ext_x_version):
            _parse_simple_parameter(line, data)
        elif line.startswith(protocol.ext_x_allow_cache):
            _parse_simple_parameter(line, data)

        elif line.startswith(protocol.ext_x_key):
            state['current_key'] = _parse_key(line)
            data['key'] = data.get('key', state['current_key'])

        elif line.startswith(protocol.extinf):
            _parse_extinf(line, data, state)
            state['expect_segment'] = True

        elif line.startswith(protocol.ext_x_stream_inf):
            state['expect_playlist'] = True
            _parse_stream_inf(line, data, state)

        elif line.startswith(protocol.ext_x_i_frame_stream_inf):
            _parse_i_frame_stream_inf(line, data)

        elif line.startswith(protocol.ext_x_media):
            _parse_media(line, data, state)

        elif line.startswith(protocol.ext_x_playlist_type):
            _parse_simple_parameter(line, data)

        elif line.startswith(protocol.ext_i_frames_only):
            data['is_i_frames_only'] = True

        elif line.startswith(protocol.ext_x_endlist):
            data['is_endlist'] = True

    return data


def extract_params(line):
    """
    Extracts parameters from a formatted input string.

    Args:
        - line (str): The string containing the parameters to extract.

    Returns:
        dict or None: A dictionary containing the extracted parameters with their respective values.
    """
    params = {}
    matches = re.findall(r'([A-Z\-]+)=("[^"]*"|[^",\s]*)', line)
    if not matches:
        return None
    for match in matches:
        param, value = match
        params[param] = value.strip('"')
    return params

def _parse_key(line):
    """
    Parses the #EXT-X-KEY line and extracts key attributes.

    Args:
        - line (str): The #EXT-X-KEY line from the playlist.

    Returns:
        dict: A dictionary containing the key attributes.
    """
    params = ATTRIBUTELISTPATTERN.split(line.replace(protocol.ext_x_key + ':', ''))[1::2]
    key = {}
    for param in params:
        name, value = param.split('=', 1)
        key[normalize_attribute(name)] = remove_quotes(value)
    return key

def _parse_extinf(line, data, state):
    """
    Parses the #EXTINF line and extracts segment duration and title.

    Args:
        - line (str): The #EXTINF line from the playlist.
        - data (dict): The dictionary to store the parsed data.
        - state (dict): The parsing state.
    """
    duration, title = line.replace(protocol.extinf + ':', '').split(',')
    state['segment'] = {'duration': float(duration), 'title': remove_quotes(title)}

def _parse_ts_chunk(line, data, state):
    """
    Parses a segment URI line and adds it to the segment list.

    Args:
        line (str): The segment URI line from the playlist.
        data (dict): The dictionary to store the parsed data.
        state (dict): The parsing state.
    """
    segment = state.pop('segment')
    if state.get('current_program_date_time'):
        segment['program_date_time'] = state['current_program_date_time']
        state['current_program_date_time'] += datetime.timedelta(seconds=segment['duration'])
    segment['uri'] = line
    segment['discontinuity'] = state.pop('discontinuity', False)
    if state.get('current_key'):
      segment['key'] = state['current_key']
    data['segments'].append(segment)

def _parse_attribute_list(prefix, line, atribute_parser):
    """
    Parses a line containing a list of attributes and their values.

    Args:
        - prefix (str): The prefix to identify the line.
        - line (str): The line containing the attributes.
        - atribute_parser (dict): A dictionary mapping attribute names to parsing functions.

    Returns:
        dict: A dictionary containing the parsed attributes.
    """
    params = ATTRIBUTELISTPATTERN.split(line.replace(prefix + ':', ''))[1::2]

    attributes = {}
    for param in params:
        name, value = param.split('=', 1)
        name = normalize_attribute(name)

        if name in atribute_parser:
            value = atribute_parser[name](value)

        attributes[name] = value

    return attributes

def _parse_stream_inf(line, data, state):
    """
    Parses the #EXT-X-STREAM-INF line and extracts stream information.

    Args:
        - line (str): The #EXT-X-STREAM-INF line from the playlist.
        - data (dict): The dictionary to store the parsed data.
        - state (dict): The parsing state.
    """
    data['is_variant'] = True
    atribute_parser = remove_quotes_parser('codecs', 'audio', 'video', 'subtitles')
    atribute_parser["program_id"] = int
    atribute_parser["bandwidth"] = int
    state['stream_info'] = _parse_attribute_list(protocol.ext_x_stream_inf, line, atribute_parser)

def _parse_i_frame_stream_inf(line, data):
    """
    Parses the #EXT-X-I-FRAME-STREAM-INF line and extracts I-frame stream information.

    Args:
        - line (str): The #EXT-X-I-FRAME-STREAM-INF line from the playlist.
        - data (dict): The dictionary to store the parsed data.
    """
    atribute_parser = remove_quotes_parser('codecs', 'uri')
    atribute_parser["program_id"] = int
    atribute_parser["bandwidth"] = int
    iframe_stream_info = _parse_attribute_list(protocol.ext_x_i_frame_stream_inf, line, atribute_parser)
    iframe_playlist = {'uri': iframe_stream_info.pop('uri'),
                       'iframe_stream_info': iframe_stream_info}

    data['iframe_playlists'].append(iframe_playlist)

def _parse_media(line, data, state):
    """
    Parses the #EXT-X-MEDIA line and extracts media attributes.

    Args:
        - line (str): The #EXT-X-MEDIA line from the playlist.
        - data (dict): The dictionary to store the parsed data.
        - state (dict): The parsing state.
    """
    quoted = remove_quotes_parser('uri', 'group_id', 'language', 'name', 'characteristics')
    media = _parse_attribute_list(protocol.ext_x_media, line, quoted)
    data['media'].append(media)

def _parse_variant_playlist(line, data, state):
    """
    Parses a variant playlist line and extracts playlist information.

    Args:
        - line (str): The variant playlist line from the playlist.
        - data (dict): The dictionary to store the parsed data.
        - state (dict): The parsing state.
    """
    playlist = {'uri': line, 'stream_info': state.pop('stream_info')}

    data['playlists'].append(playlist)

def _parse_byterange(line, state):
    """
    Parses the #EXT-X-BYTERANGE line and extracts byte range information.

    Args:
        - line (str): The #EXT-X-BYTERANGE line from the playlist.
        - state (dict): The parsing state.
    """
    state['segment']['byterange'] = line.replace(protocol.ext_x_byterange + ':', '')

def _parse_simple_parameter_raw_value(line, cast_to=str, normalize=False):
    """
    Parses a line containing a simple parameter and its value.

    Args:
        - line (str): The line containing the parameter and its value.
        - cast_to (type): The type to which the value should be cast.
        - normalize (bool): Whether to normalize the parameter name.

    Returns:
        tuple: A tuple containing the parameter name and its value.
    """
    param, value = line.split(':', 1)
    param = normalize_attribute(param.replace('#EXT-X-', ''))
    if normalize:
        value = normalize_attribute(value)
    return param, cast_to(value)

def _parse_and_set_simple_parameter_raw_value(line, data, cast_to=str, normalize=False):
    """
    Parses a line containing a simple parameter and its value, and sets it in the data dictionary.

    Args:
        - line (str): The line containing the parameter and its value.
        - data (dict): The dictionary to store the parsed data.
        - cast_to (type): The type to which the value should be cast.
        - normalize (bool): Whether to normalize the parameter name.

    Returns:
        The parsed value.
    """
    param, value = _parse_simple_parameter_raw_value(line, cast_to, normalize)
    data[param] = value
    return data[param]

def _parse_simple_parameter(line, data, cast_to=str):
    """
    Parses a line containing a simple parameter and its value, and sets it in the data dictionary.

    Args:
        line (str): The line containing the parameter and its value.
        data (dict): The dictionary to store the parsed data.
        cast_to (type): The type to which the value should be cast.

    Returns:
        The parsed value.
    """
    return _parse_and_set_simple_parameter_raw_value(line, data, cast_to, True)