

from earthkit.maps import _data


EARTHKIT_COLORS = _data.load("colors/earthkit.yaml")


def parse_colors(colors):
    parsed_colors = []
    for color in colors:
        parsed_colors.append(EARTHKIT_COLORS.get(color, color))
    return parsed_colors