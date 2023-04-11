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

from earthkit.maps import domains


def test_crs_from_string():
    crs = ccrs.PlateCarree()

    assert domains.crs_from_string("PlateCarree") == crs

    with pytest.raises(ValueError) as e_info:  # noqa: F841
        domains.crs_from_string("foobarbaz")


def test_crs_from_dict():
    crs = ccrs.PlateCarree(central_longitude=50)

    assert (
        domains.crs_from_dict({"name": "PlateCarree", "central_longitude": 50}) == crs
    )


def test_parse_crs():
    crs = ccrs.PlateCarree()
    assert domains.parse_crs("PlateCarree") == crs

    crs = ccrs.PlateCarree(central_longitude=50)
    assert domains.parse_crs({"name": "PlateCarree", "central_longitude": 50}) == crs

    crs = domains.DEFAULT_CRS
    assert domains.parse_crs(None) == crs
