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


def test_MagicsStyle_list_levels():
    magics_style = {
        "contour_level_selection_type": "list",
        "contour_level_list": "1/2/3/4/5.5",
    }
    assert MagicsStyle(**magics_style).levels == [1, 2, 3, 4, 5.5]


def test_MagicsStyle_interval_levels():
    interval_magics_style = {
        "contour_level_selection_type": "interval",
        "contour_interval": 8,
    }
    interval_style = MagicsStyle(**interval_magics_style)
    assert interval_style.levels._step == 8
    assert interval_style.levels._reference is None

    interval_and_reference_magics_style = {
        "contour_level_selection_type": "interval",
        "contour_interval": 3,
        "contour_reference_level": 2,
    }
    interval_and_reference_style = MagicsStyle(**interval_and_reference_magics_style)
    assert interval_and_reference_style.levels._step == 3
    assert interval_and_reference_style.levels._reference == 2
