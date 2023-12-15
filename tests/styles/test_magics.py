# Copyright 2023, European Centre for Medium Range Weather Forecasts.
#
# Licensed under the Apache License, Version 2.0 (the "License");
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


from earthkit.maps.styles.magics import MagicsStyle

MAGICS_STYLE = {
    "contour": "off",
    "contour_description": "Method : Area fill Level range : -48 to 56 Interval : 4 Thickness : 3 Colour : All colours Used for temperature",
    "contour_hilo": "off",
    "contour_interval": "4",
    "contour_label": "off",
    "contour_legend_text": "Contour shade (Range: -48 / 56)",
    "contour_level_selection_type": "interval",
    "contour_line_contour": "dot",
    "contour_line_thickness": 3,
    "contour_shade": "on",
    "contour_shade_colour_list": "rgb(0,0,0.5)/rgb(0,0,0.5)/rgb(0,0,0.5)/rgb(0,0,0.5)/rgb(0,0,0.5)/rgb(0,0,0.85)/rgb(0.25,0,1)/blue_purple/greenish_blue/blue_green/bluish_green/yellow_green/greenish_yellow/yellow/orangish_yellow/orange_yellow/yellowish_orange/orange/reddish_orange/red_orange/orangish_red/red/magenta/magenta/magenta/magenta/magenta",
    "contour_shade_colour_method": "list",
    "contour_shade_max_level": 56,
    "contour_shade_method": "area_fill",
    "contour_shade_min_level": -48,
    "contour_title": "Contour shade (Range: -48 / 56)",
    "grib_missing_value_indicator": 9999,
}


def test_MagicsStyle_contour_levels_():
    style = MagicsStyle(**MAGICS_STYLE)
    assert style.levels.tolist() == list(range(-48, 56 + 4, 4))


def test_MagicsStyle_contour_colours():
    style = MagicsStyle(**MAGICS_STYLE)
    assert style.colors == [
        "#000080",
        "#000080",
        "#000080",
        "#000080",
        "#000080",
        "#0000d9",
        "#4000ff",
        "#8000ff",
        "#0080ff",
        "#00ffff",
        "#00ff80",
        "#80ff00",
        "#daff00",
        "#ffff00",
        "#fff500",
        "#ffda00",
        "#ffb000",
        "#ff8000",
        "#ff4f00",
        "#ff2500",
        "#ff0a00",
        "#ff0000",
        "#ff00ff",
        "#ff00ff",
        "#ff00ff",
        "#ff00ff",
        "#ff00ff",
    ]
