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

from earthkit.maps.domains import bounds


def test_from_bbox():
    assert bounds.from_bbox([-20, 40, -30, 50], ccrs.PlateCarree()) == [
        -20,
        40,
        -30,
        50,
    ]

    assert bounds.from_bbox(
        [-20, 40, -30, 50], ccrs.LambertAzimuthalEqualArea()
    ) == pytest.approx([-1985512, 3896680, -3476561, 5630595], 1)

    assert bounds.from_bbox(
        [-1985512, 3896680, -3476561, 5630595],
        ccrs.PlateCarree(),
        ccrs.LambertAzimuthalEqualArea(),
    ) == pytest.approx([-20, 40, -30, 50], 1)
