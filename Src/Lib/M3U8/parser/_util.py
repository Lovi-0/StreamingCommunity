# 19.04.24

import itertools


def remove_quotes_parser(*attrs):
    """
    Returns a dictionary mapping attribute names to a function that removes quotes from their values.
    """
    return dict(zip(attrs, itertools.repeat(remove_quotes)))


def remove_quotes(string):
    """
    Removes quotes from a string.
    """
    quotes = ('"', "'")
    if string and string[0] in quotes and string[-1] in quotes:
        return string[1:-1]
    return string


def normalize_attribute(attribute):
    """
    Normalizes an attribute name by converting hyphens to underscores and converting to lowercase.
    """
    return attribute.replace('-', '_').lower().strip()

