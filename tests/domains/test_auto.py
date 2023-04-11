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

from earthkit.maps.domains import auto


def test_preset():
    expected_bounds = [2502500, 7497500, 752500, 5497500]
    expected_crs = ccrs.LambertAzimuthalEqualArea(
        central_latitude=52,
        central_longitude=10,
        false_easting=4321000,
        false_northing=3210000,
    )

    bounds, crs = auto.get_bounds_and_crs("europe")

    assert bounds == expected_bounds
    assert crs == expected_crs


def test_country():
    expected_bounds = [-626161, 690812, -625183, 649633]
    expected_crs_params = {
        "ellps": "WGS84",
        "proj": "aea",
        "lon_0": 2.5,
        "lat_0": 46.3,
        "x_0": 0.0,
        "y_0": 0.0,
        "lat_1": 42.9,
        "lat_2": 49.6,
    }

    bounds, crs = auto.get_bounds_and_crs("france")

    assert bounds == pytest.approx(expected_bounds, 0.5)

    crs_params = crs.proj4_params
    for key in expected_crs_params:
        if isinstance(crs_params[key], (int, float)):
            assert crs_params[key] == pytest.approx(expected_crs_params[key], 1)
        else:
            assert crs_params[key] == expected_crs_params[key]


def test_alias():
    expected_bounds = [-363796, 373425, -541558, 545791]
    expected_crs_params = {
        "ellps": "WGS84",
        "proj": "aea",
        "lon_0": -2.9,
        "lat_0": 54.3,
        "x_0": 0.0,
        "y_0": 0.0,
        "lat_1": 51.3,
        "lat_2": 57.2,
    }

    bounds, crs = auto.get_bounds_and_crs("UK")

    assert bounds == pytest.approx(expected_bounds, 0.5)

    crs_params = crs.proj4_params
    for key in expected_crs_params:
        if isinstance(crs_params[key], (int, float)):
            assert crs_params[key] == pytest.approx(expected_crs_params[key], 1)
        else:
            assert crs_params[key] == expected_crs_params[key]


def test_get_optimal_crs():
    bounds = [-25, 40, 32, 72]
    expected_crs_params = {
        "ellps": "WGS84",
        "proj": "aea",
        "lon_0": 7.5,
        "lat_0": 52.0,
        "x_0": 0.0,
        "y_0": 0.0,
        "lat_1": 38.4,
        "lat_2": 65.6,
    }

    crs = auto.get_optimal_crs(bounds)

    assert crs.proj4_params == expected_crs_params


def test_get_crs_extents():
    bounds = [-25, 40, 32, 72]
    crs = ccrs.AlbersEqualArea(
        central_latitude=52, central_longitude=7.5, standard_parallels=(38.4, 65.6)
    )

    expected_bounds = [-3046054.6, 3046054.6, -2239135.9, 2497907.6]

    result = auto.get_crs_extents(bounds, crs)

    assert result == pytest.approx(expected_bounds, 0.5)


def test_Extents_is_global():
    # Test whole globe
    domain = [-180, 180, -90, 90]
    extents = auto.Extents(domain)
    assert extents.is_global()

    # Test > 60% coverage but < 100%
    domain = [-150, 150, -65, 65]
    extents = auto.Extents(domain)
    assert extents.is_global()

    # Test < 60% coverage
    domain = [-140, 140, -65, 65]
    extents = auto.Extents(domain)
    assert not extents.is_global()

    # Test large threshold
    domain = [-150, 150, -65, 65]
    extents = auto.Extents(domain, large_threshold=0.7)
    assert not extents.is_global()


def test_Extents_is_equatorial():
    # Test whole globe
    domain = [-180, 180, -90, 90]
    extents = auto.Extents(domain)
    assert extents.is_equatorial()

    # Test region centred on equator
    domain = [-10, 40, -30, 30]
    extents = auto.Extents(domain)
    assert extents.is_equatorial()

    # Test region close to equator
    domain = [-30, 20, -15, 45]
    extents = auto.Extents(domain)
    assert extents.is_equatorial()

    # Test region on boundary
    domain = [-30, 20, 20, 30]
    extents = auto.Extents(domain)
    assert not extents.is_equatorial()

    # Test non-equatorial region
    domain = [-30, 20, 60, 70]
    extents = auto.Extents(domain)
    assert not extents.is_equatorial()


def test_Extents_is_polar():
    # Test whole globe
    domain = [-180, 180, -90, 90]
    extents = auto.Extents(domain)
    assert not extents.is_polar()

    # Test region centred on north pole
    domain = [-180, 180, 70, 90]
    extents = auto.Extents(domain)
    assert extents.is_polar()

    # Test region close to north pole
    domain = [-180, 180, 75, 85]
    extents = auto.Extents(domain)
    assert extents.is_polar()

    # Test region centred on south pole
    domain = [-180, 180, -90, -70]
    extents = auto.Extents(domain)
    assert extents.is_polar()

    # Test region on boundary
    domain = [-180, 180, 60, 90]
    extents = auto.Extents(domain)
    assert not extents.is_polar()

    # Test non-polar region
    domain = [-10, 40, 30, 70]
    extents = auto.Extents(domain)
    assert not extents.is_polar()


def test_Extents_is_portrait_landscape_square():
    # Test portrait
    domain = [-10, 20, 30, 90]
    extents = auto.Extents(domain)
    assert extents.is_portrait()
    assert not extents.is_landscape()
    assert not extents.is_square()

    # Test just above portrait boundary
    domain = [-10, 20, 30, 69]
    extents = auto.Extents(domain)
    assert extents.is_portrait()
    assert not extents.is_landscape()
    assert not extents.is_square()

    # Test on portrait boundary
    domain = [-10, 20, 30, 66]
    extents = auto.Extents(domain)
    assert not extents.is_portrait()
    assert not extents.is_landscape()
    assert extents.is_square()

    # Test landscape
    domain = [-30, 20, 30, 60]
    extents = auto.Extents(domain)
    assert not extents.is_portrait()
    assert extents.is_landscape()
    assert not extents.is_square()

    # Test just above landscape boundary
    domain = [-19, 20, 30, 60]
    extents = auto.Extents(domain)
    assert not extents.is_portrait()
    assert extents.is_landscape()
    assert not extents.is_square()

    # Test on landscape boundary
    domain = [-16, 20, 30, 66]
    extents = auto.Extents(domain)
    assert not extents.is_portrait()
    assert not extents.is_landscape()
    assert extents.is_square()

    # Test square
    domain = [-10, 20, 30, 60]
    extents = auto.Extents(domain)
    assert not extents.is_portrait()
    assert not extents.is_landscape()
    assert extents.is_square()


def test_Extents_is_large_small():
    # Test whole globe
    domain = [-180, 180, -90, 90]
    extents = auto.Extents(domain)
    assert not extents.is_large()
    assert not extents.is_small()

    # Test > 60% coverage but < 100%
    domain = [-150, 150, -65, 65]
    extents = auto.Extents(domain)
    assert not extents.is_large()
    assert not extents.is_small()

    # Test < 60% coverage
    domain = [-140, 140, -65, 65]
    extents = auto.Extents(domain)
    assert extents.is_large()
    assert not extents.is_small()

    # Test > 20% coverage byt < 60%
    domain = [-100, 100, -40, 30]
    extents = auto.Extents(domain)
    assert extents.is_large()
    assert not extents.is_small()

    # Test 20% coverage
    domain = [-80, 80, -40, 40]
    extents = auto.Extents(domain)
    assert not extents.is_large()
    assert extents.is_small()
