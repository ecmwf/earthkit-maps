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

from earthkit.maps.domains import optimal


def test_Extents_area():
    extents = optimal.Extents([-50, 50, -30, 30])
    assert extents.area == 6000

    extents_wraps_globe = optimal.Extents([130, -130, -30, 30])
    assert extents_wraps_globe.area == 6000

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.area == 64800

    extents_null = optimal.Extents([-10, -10, 5, 5])
    assert extents_null.area == 0


def test_Extents_ratio():
    extents = optimal.Extents([-30, 30, -30, 30])
    assert extents.ratio == 1

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.ratio == 2

    extents_null = optimal.Extents([-10, -10, 5, 5])
    assert extents_null.ratio == 0


def test_Extents_standard_parallels():
    extents_northern_hemisphere = optimal.Extents([-20, 40, 30, 70])
    assert extents_northern_hemisphere.standard_parallels == (36.4, 63.6)

    extents_southern_hemisphere = optimal.Extents([-150, -70, -70, -30])
    assert extents_southern_hemisphere.standard_parallels == (-63.6, -36.4)


def test_Extents_central_lat():
    extents_northern_hemisphere = optimal.Extents([-20, 40, 30, 70])
    assert extents_northern_hemisphere.central_lat == 50

    extents_southern_hemisphere = optimal.Extents([-150, -70, -70, -30])
    assert extents_southern_hemisphere.central_lat == -50

    extents_equatorial = optimal.Extents([-150, -70, -30, 30])
    assert extents_equatorial.central_lat == 0

    extents_polar = optimal.Extents([-150, -70, 90, 90])
    assert extents_polar.central_lat == 90


def test_Extents_central_lon():
    extents_northern_hemisphere = optimal.Extents([-20, 40, 30, 70])
    assert extents_northern_hemisphere.central_lon == 10

    extents_southern_hemisphere = optimal.Extents([-150, -70, -70, -30])
    assert extents_southern_hemisphere.central_lon == -110

    extents_wraps_globe_positive = optimal.Extents([150, 230, -30, 30])
    assert extents_wraps_globe_positive.central_lon == 190

    extents_wraps_globe_switch = optimal.Extents([150, -130, -30, 30])
    assert extents_wraps_globe_switch.central_lon == 190


def test_Extents_is_landscape():
    extents_square = optimal.Extents([-30, 30, -30, 30])
    assert extents_square.is_landscape() is False

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.is_landscape() is True

    extents_tall = optimal.Extents([-30, 10, 10, 70])
    assert extents_tall.is_landscape() is False


def test_Extents_is_portrait():
    extents_square = optimal.Extents([-30, 30, -30, 30])
    assert extents_square.is_portrait() is False

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.is_portrait() is False

    extents_tall = optimal.Extents([-30, 10, 10, 70])
    assert extents_tall.is_portrait() is True


def test_Extents_is_square():
    extents_square = optimal.Extents([-30, 30, -30, 30])
    assert extents_square.is_square() is True

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.is_square() is False

    extents_tall = optimal.Extents([-30, 10, 10, 70])
    assert extents_tall.is_square() is False


def test_Extents_is_global():
    extents_square = optimal.Extents([-30, 30, -30, 30])
    assert extents_square.is_global() is False

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.is_global() is True

    extents_almost_global = optimal.Extents([-170, 170, -80, 80])
    assert extents_almost_global.is_global() is True

    extents_tall = optimal.Extents([-30, 10, 10, 70])
    assert extents_tall.is_global() is False


def test_Extents_is_large():
    extents_square = optimal.Extents([-30, 30, -30, 30])
    assert extents_square.is_large() is False

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.is_large() is False

    extents_large = optimal.Extents([-100, 90, -80, 80])
    assert extents_large.is_large() is True

    extents_tall = optimal.Extents([-30, 10, 10, 70])
    assert extents_tall.is_large() is False


def test_Extents_is_small():
    extents_square = optimal.Extents([-30, 30, -30, 30])
    assert extents_square.is_small() is True

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.is_small() is False

    extents_tall = optimal.Extents([-30, 10, 10, 70])
    assert extents_tall.is_small() is True


def test_Extents_is_polar():
    extents_square = optimal.Extents([-30, 30, -30, 30])
    assert extents_square.is_polar() is False

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.is_polar() is False

    extents_polar = optimal.Extents([-150, -70, 90, 90])
    assert extents_polar.is_polar() is True


def test_Extents_is_equatorial():
    extents_square = optimal.Extents([-30, 30, -30, 30])
    assert extents_square.is_equatorial() is True

    extents_global = optimal.Extents([-180, 180, -90, 90])
    assert extents_global.is_equatorial() is True

    extents_polar = optimal.Extents([-150, -70, 90, 90])
    assert extents_polar.is_equatorial() is False


def test_global():
    assert isinstance(
        optimal.crs_from_bounds([-180, 180, -90, 90]),
        ccrs.PlateCarree,
    )


def test_equatorial():
    assert isinstance(
        optimal.crs_from_bounds([-70, -20, -31, 29]),
        ccrs.PlateCarree,
    )


def test_north_polar():
    assert isinstance(
        optimal.crs_from_bounds([-180, 180, 70, 90]),
        ccrs.NorthPolarStereo,
    )


def test_south_polar():
    assert isinstance(
        optimal.crs_from_bounds([-180, 180, -90, -70]),
        ccrs.SouthPolarStereo,
    )


def test_landscape():
    assert isinstance(
        optimal.crs_from_bounds([-70, 30, 30, 70]),
        ccrs.AlbersEqualArea,
    )


def test_portrait():
    assert isinstance(
        optimal.crs_from_bounds([0, 30, 30, 70]),
        ccrs.TransverseMercator,
    )
