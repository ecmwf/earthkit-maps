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
from earthkit.data.utils.bbox import BoundingBox

from earthkit.maps.domains import parse


def test_parse_string():
    domain = parse("France", None)

    assert domain.domain_name == "France"
    assert domain.bounds == pytest.approx([-626161, 690812, -625183, 649633], 1)
    assert isinstance(domain.crs, ccrs.AlbersEqualArea)


def test_parse_None():
    domain = parse(None, None)

    assert domain.domain_name is None
    assert isinstance(domain.crs, ccrs.PlateCarree)


def test_parse_extents():
    domain = parse([-20, 40, 30, 72], None)
    assert isinstance(domain.crs, ccrs.AlbersEqualArea)


def test_parse_crs():
    domain = parse(None, crs=ccrs.EckertIV())
    assert isinstance(domain.crs, ccrs.EckertIV)


def test_parse_bbox():
    domain = parse(BoundingBox(north=72, south=30, east=-20, west=40), None)
    assert domain.bounds == pytest.approx([-6932732, 6932732, -2352422, 6281727], 1)
    assert isinstance(domain.crs, ccrs.AlbersEqualArea)
