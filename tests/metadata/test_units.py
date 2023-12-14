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

import pytest

from earthkit.maps.metadata import units


@pytest.mark.skipif(units._NO_CF_UNITS, reason="cf-units is not installed")
def test_are_equal():
    assert units.are_equal("K", "kelvin") is True
    assert units.are_equal("celsius", "kelvin") is False


@pytest.mark.skipif(units._NO_CF_UNITS, reason="cf-units is not installed")
def test_convert():
    assert units.convert(273.15, "kelvin", "celsius") == 0


@pytest.mark.skipif(units._NO_CF_UNITS, reason="cf-units is not installed")
def test_anomaly_equivalence():
    assert units.anomaly_equivalence("celsius") is True
    assert units.anomaly_equivalence("kelvin") is True
    assert units.anomaly_equivalence("fahrenheit") is False


def test_format_units_no_cf_units():
    _no_cf_units = units._NO_CF_UNITS
    units._NO_CF_UNITS = True
    assert units.format_units("celsius") == "$°C$"
    units._NO_CF_UNITS = _no_cf_units


@pytest.mark.skipif(units._NO_CF_UNITS, reason="cf-units is not installed")
def test_format_units_with_cf_units():
    assert units.format_units("celsius") == "$°C$"
    assert units.format_units("s-1") == "${s}^{-1}$"
