import os
from functools import partial
from pathlib import Path

import cartopy
import matplotlib
import pytest

from earthkit.maps import charts, schema


# TODO: There is a bug in matplotlib causing an incorrect DeprecationWarning
# to be raised; ignore for now, but update when matplotlib has fixed this bug
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_Chart_queue():
    chart = charts.Chart()

    assert len(chart._queue) == 0

    chart.coastlines()
    assert len(chart._queue) == 1
    assert chart._queue[0][1] == tuple()
    assert chart._queue[0][2] == dict()

    chart._release_queue()
    assert len(chart._queue) == 0


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_Chart_bounds_and_crs():
    chart = charts.Chart()
    assert chart.bounds is None
    assert chart.crs == schema.reference_crs

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
    chart = charts.Chart(domain="United Kingdom")
    assert chart.bounds == pytest.approx(expected_bounds, 0.5)
    crs_params = chart.crs.proj4_params
    for key in expected_crs_params:
        if isinstance(crs_params[key], (int, float)):
            assert crs_params[key] == pytest.approx(expected_crs_params[key], 1)
        else:
            assert crs_params[key] == expected_crs_params[key]


@pytest.fixture
def dummy_chart():
    path = Path(__file__).parent / "temporary-chart.png"
    chart = charts.Chart()
    chart.temporary_save = partial(chart.save, path)
    yield chart
    os.remove(path)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_Chart_coastlines(dummy_chart):
    basic_children = dummy_chart.axis.get_children()

    dummy_chart.coastlines()
    dummy_chart.temporary_save()
    new_children = dummy_chart.axis.get_children()
    assert len(new_children) == len(basic_children) + 1
    assert isinstance(new_children[0], cartopy.mpl.feature_artist.FeatureArtist)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_Chart_gridlines(dummy_chart):
    basic_children = dummy_chart.axis.get_children()

    dummy_chart.gridlines()
    dummy_chart.temporary_save()
    new_children = dummy_chart.axis.get_children()
    assert len(new_children) > len(basic_children)
    assert isinstance(new_children[0], matplotlib.collections.LineCollection)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_Chart_borders(dummy_chart):
    basic_children = dummy_chart.axis.get_children()

    dummy_chart.borders()
    dummy_chart.temporary_save()
    new_children = dummy_chart.axis.get_children()
    assert len(new_children) == len(basic_children) + 1
    assert isinstance(new_children[0], cartopy.mpl.feature_artist.FeatureArtist)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_Chart_land(dummy_chart):
    basic_children = dummy_chart.axis.get_children()

    dummy_chart.land()
    dummy_chart.temporary_save()
    new_children = dummy_chart.axis.get_children()
    assert len(new_children) == len(basic_children) + 1
    assert isinstance(new_children[0], cartopy.mpl.feature_artist.FeatureArtist)
