
from earthkit.maps import Chart


DEFAULT_WORKFLOW = {
    "coastlines": dict(),
    "gridlines": dict(),
    "title": dict(),
    "legend": dict(),
}


def quickplot(data, workflow=None, **kwargs):
    workflow = {**DEFAULT_WORKFLOW, **(workflow or dict())}
    
    chart = Chart(**kwargs)
    chart.shaded_contour(data)
    
    for step, step_kwargs in workflow.items():
        getattr(chart, step)(**step_kwargs)
    
    chart.show()