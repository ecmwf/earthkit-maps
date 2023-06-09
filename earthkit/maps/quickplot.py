from earthkit.maps import Chart
from earthkit.maps.schema import schema

DEFAULT_WORKFLOW = {
    "coastlines": dict(),
    "borders": dict(),
    "gridlines": dict(),
    "subplot_titles": dict(),
    "legend": dict(),
}


@schema.apply("cmap")
def quickplot(data, workflow=None, units=None, levels=None, cmap=None, **kwargs):
    workflow = {**DEFAULT_WORKFLOW, **(workflow or dict())}

    chart = Chart(**kwargs)
    chart.shaded_contour(data, levels=levels, cmap=cmap, units=units)

    for step, step_kwargs in workflow.items():
        getattr(chart, step)(**step_kwargs)

    chart.show()
