# 16.05.24


# Internal utilities
from .alphabet import alpha_mappings
from .symbols import symbols_mapping
from .math_symbol import math_symbols_mapping
from .misc_symbols import misc_symbols_mapping
from .quantifiers import quantifiers_mapping
from .geometry import geometry_mapping
from .additional_math import additional_math_mapping
from .currency import currency_mapping
from .units_of_measurement import units_of_measurement_mapping
from .other import miscellaneous_symbols_mapping


all_mappings = {
    **alpha_mappings,
    **symbols_mapping, 
    **math_symbols_mapping,
    **misc_symbols_mapping,
    **quantifiers_mapping,
    **geometry_mapping,
    **additional_math_mapping,
    **currency_mapping,
    **units_of_measurement_mapping,
    **miscellaneous_symbols_mapping
}



def transliterate(text):
    translated_text = ''.join(all_mappings.get(c, c) for c in text)
    return translated_text

