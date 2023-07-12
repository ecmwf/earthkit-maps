from earthkit.maps import Chart

WORKFLOW = [
    "coastlines",
    "land",
    "borders",
    "gridlines",
]


def quickplot(data=None, **kwargs):
    chart = Chart(**kwargs)

    if data is not None:
        raise NotImplementedError

    for item in WORKFLOW:
        getattr(chart, item)()

    chart.show()
