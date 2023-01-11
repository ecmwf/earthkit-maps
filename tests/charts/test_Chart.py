import pytest

from magpye import charts, schema


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
