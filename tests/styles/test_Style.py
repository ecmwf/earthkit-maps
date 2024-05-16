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

import numpy as np
import pytest

from earthkit.maps import styles
from earthkit.maps.metadata import units


def test_Style_static_levels():
    style = styles.Style(levels=[1, 2, 3])
    assert style.levels([1]) == [1, 2, 3]
    assert style.levels([-19999]) == [1, 2, 3]
    assert style.levels(range(9999)) == [1, 2, 3]


def test_Style_levels():
    static_style = styles.Style(levels=[1, 2, 3])
    assert static_style.levels() == [1, 2, 3]

    range_style = styles.Style(levels=range(-10, 11, 5))
    assert range_style.levels() == range(-10, 11, 5)

    dynamic_style = styles.Style()
    with pytest.raises(ValueError):
        dynamic_style.levels()


@pytest.mark.skipif(units._NO_CF_UNITS, reason="cf-units is not installed")
def test_Style_units():
    style = styles.Style(units="celsius")
    assert style.units == "$°C$"


@pytest.mark.skipif(units._NO_CF_UNITS, reason="cf-units is not installed")
def test_Style_convert_units():
    style = styles.Style(units="celsius")
    assert style.convert_units(273.15, source_units="kelvin") == 0


@pytest.mark.skipif(units._NO_CF_UNITS, reason="cf-units is not installed")
def test_Style_convert_units_anomaly():
    style = styles.Style(units="celsius")
    assert (
        style.convert_units(-5, source_units="kelvin", short_name="temperature_anomaly")
        == -5
    )


def test_Style_values_to_colors():
    style = styles.Style(levels=[1, 2, 3, 4], colors=["red", "green", "blue"])
    assert style.values_to_colors(2.7) == (0.0, 0.5019607843137255, 0.0, 1.0)
    assert style.values_to_colors(3) == (0.0, 0.0, 1.0, 1.0)
    assert style.values_to_colors(0.25) == (1.0, 0.0, 0.0, 1.0)
    assert style.values_to_colors(np.nan) == (0.0, 0.0, 0.0, 0.0)
    assert style.values_to_colors([0.25, np.nan]).tolist() == [
        [1.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0],
    ]
