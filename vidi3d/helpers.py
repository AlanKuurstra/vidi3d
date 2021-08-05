from collections import namedtuple

import numpy as np

from .definitions import ImageDisplayType

Event = namedtuple('Event', ['x', 'y'])


def apply_display_type(complex_values, display_type):
    if display_type == ImageDisplayType.mag:
        data = np.abs(complex_values)
    elif display_type == ImageDisplayType.phase:
        data = np.angle(complex_values)
    elif display_type == ImageDisplayType.real:
        data = np.real(complex_values)
    elif display_type == ImageDisplayType.imag:
        data = np.imag(complex_values)
    else:
        raise ValueError("Display type not recognized")
    return data
