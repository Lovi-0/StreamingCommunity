# 04.04.24

import os
import logging
import importlib.util


# Variable
Cache = {}


class UnidecodeError(ValueError):
    pass


def transliterate_nonascii(string: str, errors: str = 'ignore', replace_str: str = '?') -> str:
    """Transliterates non-ASCII characters in a string to their ASCII counterparts.

    Args:
        string (str): The input string containing non-ASCII characters.
        errors (str): Specifies the treatment of errors. Can be 'ignore', 'strict', 'replace', or 'preserve'.
        replace_str (str): The replacement string used when errors='replace'.

    Returns:
        str: The transliterated string with non-ASCII characters replaced.
    """
    return _transliterate(string, errors, replace_str)


def _get_ascii_representation(char: str) -> str:
    """Obtains the ASCII representation of a Unicode character.

    Args:
        char (str): The Unicode character.

    Returns:
        str: The ASCII representation of the character.
    """
    codepoint = ord(char)

    # If the character is ASCII, return it as is
    if codepoint < 0x80:
        return str(char)

    # Ignore characters outside the BMP (Basic Multilingual Plane)
    if codepoint > 0xeffff:
        return None

    # Warn about surrogate characters
    if 0xd800 <= codepoint <= 0xdfff:
        logging.warning("Surrogate character %r will be ignored. "
                        "You might be using a narrow Python build.", char)

    # Calculate section and position
    section = codepoint >> 8
    position = codepoint % 256 

    try:
        # Look up the character in the cache
        table = Cache[section]
        
    except KeyError:
        try:
            # Import the module corresponding to the section
            module_name = f"x{section:03x}.py"
            main = os.path.abspath(os.path.dirname(__file__))
            module_path = os.path.join(main, module_name)
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        except ImportError:
            # If module import fails, set cache entry to None and return
            Cache[section] = None
            return None

        # Update cache with module data
        Cache[section] = table = module.data

    # Return the ASCII representation if found, otherwise None
    if table and len(table) > position:
        return table[position]
    else:
        return None


def _transliterate(string: str, errors: str, replace_str: str) -> str:
    """Main transliteration function.

    Args:
        string (str): The input string.
        errors (str): Specifies the treatment of errors. Can be 'ignore', 'strict', 'replace', or 'preserve'.
        replace_str (str): The replacement string used when errors='replace'.

    Returns:
        str: The transliterated string.
    """
    retval = []

    for char in string:
        # Get the ASCII representation of the character
        ascii_char = _get_ascii_representation(char)

        if ascii_char is None:
            # Handle errors based on the specified policy
            if errors == 'ignore':
                ascii_char = ''
            elif errors == 'strict':
                logging.error(f'No replacement found for character {char!r}')
                raise UnidecodeError(f'no replacement found for character {char!r}')
            elif errors == 'replace':
                ascii_char = replace_str
            elif errors == 'preserve':
                ascii_char = char
            else:
                logging.error(f'Invalid value for errors parameter {errors!r}')
                raise UnidecodeError(f'invalid value for errors parameter {errors!r}')

        # Append the ASCII representation to the result
        retval.append(ascii_char)

    return ''.join(retval)


def transliterate_expect_ascii(string: str, errors: str = 'ignore', replace_str: str = '?') -> str:
    """Transliterates non-ASCII characters in a string, expecting ASCII input.

    Args:
        string (str): The input string containing non-ASCII characters.
        errors (str): Specifies the treatment of errors. Can be 'ignore', 'strict', 'replace', or 'preserve'.
        replace_str (str): The replacement string used when errors='replace'.

    Returns:
        str: The transliterated string with non-ASCII characters replaced.
    """
    try:
        # Check if the string can be encoded as ASCII
        string.encode('ASCII')
    except UnicodeEncodeError:
        # If encoding fails, fall back to transliteration
        pass
    else:
        # If the string is already ASCII, return it as is
        return string

    # Otherwise, transliterate non-ASCII characters
    return _transliterate(string, errors, replace_str)


# Out
transliterate = transliterate_expect_ascii
