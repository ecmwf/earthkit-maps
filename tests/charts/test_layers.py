
from earthkit.maps import charts


def test_layer_append():
    chart = charts.Chart()

    assert len(chart._layers) == 0

    chart.coastlines()
    assert len(chart._queue) == 1
    assert chart._queue[0][1] == tuple()
    assert chart._queue[0][2] == dict()

    chart._release_queue()
    assert len(chart._queue) == 0
