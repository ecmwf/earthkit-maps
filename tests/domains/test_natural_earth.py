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

import cartopy.crs as ccrs
import pytest

from earthkit.maps.domains import natural_earth


def test_NaturalEarthDomain_France():
    domain = natural_earth.NaturalEarthDomain("France")

    assert domain.domain_name == "France"

    assert domain.geometry.__class__.__name__ == "MultiPolygon"

    assert isinstance(domain.crs, ccrs.AlbersEqualArea)

    assert isinstance(domain.bounds, list)


def test_NaturalEarthDomain_doesnt_exist():
    with pytest.raises(ValueError):
        natural_earth.NaturalEarthDomain("Tatooine").geometry
