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
