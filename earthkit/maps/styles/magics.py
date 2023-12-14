# Copyright 2023, European Centre for Medium Range Weather Forecasts.
#
# Licensed under the Apache License, Version 2.0 (the "License"),
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast

import numpy as np
from matplotlib import colors

from earthkit.maps.styles.levels import Levels

MAGICS_COLOURS = {
    "automatic": (0.0, 0.0, 0.0),
    "none": (-1.0, -1.0, -1.0),
    "background": (1.0, 1.0, 1.0),
    "foreground": (0.0, 0.0, 0.0),
    "ecmwf_blue": (0.25, 0.43, 0.7),
    "red": (1.0000, 0.0000, 0.0000),
    "green": (0.0000, 1.0000, 0.0000),
    "blue": (0.0000, 0.0000, 1.0000),
    "yellow": (1.0000, 1.0000, 0.0000),
    "cyan": (0.0000, 1.0000, 1.0000),
    "magenta": (1.0000, 0.0000, 1.0000),
    "black": (0.0000, 0.0000, 0.0000),
    "avocado": (0.4225, 0.6500, 0.1950),
    "beige": (0.8500, 0.7178, 0.4675),
    "brick": (0.6000, 0.0844, 0.0300),
    "brown": (0.4078, 0.0643, 0.0000),
    "burgundy": (0.5000, 0.0000, 0.1727),
    "charcoal": (0.2000, 0.2000, 0.2000),
    "chestnut": (0.3200, 0.0112, 0.0000),
    "coral": (0.9000, 0.2895, 0.2250),
    "cream": (1.0000, 0.8860, 0.6700),
    "evergreen": (0.0000, 0.4500, 0.2945),
    "gold": (0.7500, 0.5751, 0.0750),
    "grey": (0.7000, 0.7000, 0.7000),
    "khaki": (0.5800, 0.4798, 0.2900),
    "kelly_green": (0.0000, 0.5500, 0.1900),
    "lavender": (0.6170, 0.4070, 0.9400),
    "mustard": (0.6000, 0.3927, 0.0000),
    "navy": (0.0000, 0.0000, 0.4000),
    "ochre": (0.6800, 0.4501, 0.0680),
    "olive": (0.3012, 0.3765, 0.0000),
    "peach": (0.9400, 0.4739, 0.3788),
    "pink": (0.9000, 0.3600, 0.4116),
    "rose": (0.8000, 0.2400, 0.4335),
    "rust": (0.7000, 0.2010, 0.0000),
    "sky": (0.4500, 0.6400, 1.0000),
    "tan": (0.4000, 0.3309, 0.2000),
    "tangerine": (0.8784, 0.4226, 0.0000),
    "turquoise": (0.1111, 0.7216, 0.6503),
    "violet": (0.4823, 0.0700, 0.7000),
    "reddish_purple": (1.0000, 0.0000, 0.8536),
    "purple_red": (1.0000, 0.0000, 0.5000),
    "purplish_red": (1.0000, 0.0000, 0.2730),
    "orangish_red": (1.0000, 0.0381, 0.0000),
    "red_orange": (1.0000, 0.1464, 0.0000),
    "reddish_orange": (1.0000, 0.3087, 0.0000),
    "orange": (1.0000, 0.5000, 0.0000),
    "yellowish_orange": (1.0000, 0.6913, 0.0000),
    "orange_yellow": (1.0000, 0.8536, 0.0000),
    "orangish_yellow": (1.0000, 0.9619, 0.0000),
    "greenish_yellow": (0.8536, 1.0000, 0.0000),
    "yellow_green": (0.5000, 1.0000, 0.0000),
    "yellowish_green": (0.1464, 1.0000, 0.0000),
    "bluish_green": (0.0000, 1.0000, 0.5000),
    "blue_green": (0.0000, 1.0000, 1.0000),
    "greenish_blue": (0.0000, 0.5000, 1.0000),
    "purplish_blue": (0.1464, 0.0000, 1.0000),
    "blue_purple": (0.5000, 0.0000, 1.0000),
    "bluish_purple": (0.8536, 0.0000, 1.0000),
    "purple": (1.0000, 0.0000, 1.0000),
    "white": (1.0000, 1.0000, 1.0000),
    "undefined": (-1.0, -1.0, -1.0),
}


class MagicsStyle:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @property
    def levels(self):
        selection_type = self.kwargs["contour_level_selection_type"]
        if selection_type == "list":
            return [float(i) for i in self.kwargs["contour_level_list"].split("/")]
        elif selection_type == "interval":
            interval = float(self.kwargs["contour_interval"])
            if "contour_shade_min_level" in self.kwargs:
                return np.arange(
                    float(self.kwargs["contour_shade_min_level"]),
                    float(self.kwargs["contour_shade_max_level"] + interval),
                    interval,
                )
            return Levels(
                step=interval,
                reference=self.kwargs.get("contour_reference_level"),
            )
        else:
            raise NotImplementedError(
                f"selection type '{selection_type}' is not yet supported"
            )

    @property
    def colors(self):
        colour_method = self.kwargs["contour_shade_colour_method"]
        if colour_method == "list":
            contour_colours = [
                parse_color(color)
                for color in self.kwargs["contour_shade_colour_list"].split("/")
            ]
        else:
            raise NotImplementedError(
                f"contour_shade_colour_method '{colour_method}' is not yet "
                f"supported"
            )
        return contour_colours


def parse_color(color):
    color = color.lower()
    if color.startswith("rgb"):
        color = ast.literal_eval(color.lstrip("rgb"))
    elif color.startswith("hsl"):
        color = colors.hsv_to_rgb(ast.literal_eval(color.lstrip("hsl")))
    else:
        color = MAGICS_COLOURS.get(color, color)
    if not isinstance(color, str):
        color = colors.rgb2hex(color)
    return color
