import cartopy.crs as ccrs
import pytest

from magpye.domains import auto


def test_europe():
    expected_bounds = [2502500, 7497500, 752500, 5497500]
    expected_crs = ccrs.LambertAzimuthalEqualArea(
        central_latitude=52,
        central_longitude=10,
        false_easting=4321000,
        false_northing=3210000,
    )

    bounds, crs = auto.get_domain_extents_and_crs("europe")

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

    bounds, crs = auto.get_domain_extents_and_crs("france")

    assert bounds == pytest.approx(expected_bounds, 0.5)

    crs_params = crs.proj4_params
    for key in expected_crs_params:
        if isinstance(crs_params[key], (int, float)):
            assert crs_params[key] == pytest.approx(expected_crs_params[key], 1)
        else:
            assert crs_params[key] == expected_crs_params[key]
