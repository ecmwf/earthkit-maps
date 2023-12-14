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

from earthkit.maps import Chart
from earthkit.maps.charts import layouts

DEFAULT_BLUEPRINT = {
    "coastlines": {},
    "borders": {},
    "gridlines": {},
    "legend": {},
    "subplot_titles": {},
}


def quickplot(
    *data,
    blueprint=DEFAULT_BLUEPRINT,
    units=None,
    style=None,
    disjoint=False,
    show=True,
    **kwargs,
):

    if disjoint and "rows" not in kwargs and "columns" not in kwargs:
        kwargs["rows"], kwargs["columns"] = layouts.rows_cols(len(data))

    chart = Chart(**kwargs)

    if units is not None:
        if not isinstance(units, (list, tuple)):
            units = [units]
        if len(units) != len(data):
            units = units + [units[-1]] * (len(data) - len(units))
    else:
        units = [None] * len(data)

    for i, (item, unit) in enumerate(zip(data, units)):
        if disjoint:
            chart.add_subplot()
            chart[i].plot(item, style=style, units=unit)
        else:
            chart.plot(item, style=style, units=unit)

    for method, method_kwargs in blueprint.items():
        getattr(chart, method)(**method_kwargs)

    if show:
        chart.show()
    else:
        return chart
