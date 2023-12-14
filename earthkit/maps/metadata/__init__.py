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

import warnings

from earthkit.maps.metadata import formatters, units
from earthkit.maps.metadata.formatters import TimeFormatter, format_month

__all__ = [
    "units",
    "formatters",
]


DEFAULT_FORECAST_TITLE = (
    "{variable_name}\n"
    "Base time: {base_time:%H:%M} on {base_time:%Y-%m-%d}   "
    "Valid time: {valid_time:%H:%M} on {valid_time:%Y-%m-%d} (T+{lead_time})"
)
DEFAULT_ANALYSIS_TITLE = (
    "{variable_name} at {valid_time:%H:%M} on {valid_time:%Y-%m-%d}"
)

TIME_KEYS = ["base_time", "valid_time", "lead_time", "time"]

MAGIC_KEYS = {
    "variable_name": {
        "preference": ["long_name", "standard_name", "name", "short_name"],
    },
    "short_name": {
        "preference": ["short_name", "name", "standard_name", "long_name"],
    },
    "month": {
        "function": format_month,
    },
}


def default_label(data):
    if data.metadata("type") == "an":
        format_string = DEFAULT_ANALYSIS_TITLE
    else:
        format_string = DEFAULT_FORECAST_TITLE
    return format_string


def extract(data, attr, default=None):

    if attr in TIME_KEYS:
        handler = TimeFormatter(data.datetime())
        label = getattr(handler, attr)[0]

    else:
        if hasattr(data, "metadata"):
            search = data.metadata
        else:
            data_key = [
                key
                for key in data.attrs["reduce_attrs"]
                if "reduce_dims" in data.attrs["reduce_attrs"][key]
            ][0]

            def search(x, default):
                return data.attrs["reduce_attrs"][data_key].get(x, default)

        candidates = [attr]
        if attr in MAGIC_KEYS:
            if "function" in MAGIC_KEYS[attr]:
                return MAGIC_KEYS[attr]["function"](data)
            else:
                candidates = MAGIC_KEYS[attr]["preference"] + candidates

        for item in candidates:
            label = search(item, default=None)
            if label is not None:
                break
        else:
            warnings.warn(f'No key "{attr}" found in layer metadata.')

    return label or default
