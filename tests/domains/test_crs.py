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

from earthkit.maps.domains import crs


def test_from_string():
    assert crs.from_string("Robinson") == ccrs.Robinson()


def test_from_dict():
    kwargs = {
        "name": "LambertAzimuthalEqualArea",
        "central_longitude": 40,
        "central_latitude": -10,
    }
    assert crs.from_dict(kwargs) == (
        ccrs.LambertAzimuthalEqualArea(
            **{k: v for k, v in kwargs.items() if k != "name"}
        )
    )


def test_parse():
    assert crs.parse(None) == ccrs.PlateCarree()

    assert crs.parse("Mollweide") == ccrs.Mollweide()

    kwargs = {
        "name": "LambertAzimuthalEqualArea",
        "central_longitude": 40,
        "central_latitude": -10,
    }
    assert crs.parse(kwargs) == (
        ccrs.LambertAzimuthalEqualArea(
            **{k: v for k, v in kwargs.items() if k != "name"}
        )
    )
