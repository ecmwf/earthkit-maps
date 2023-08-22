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

import itertools
from string import Formatter

import numpy as np
from cf_units import Unit
from cf_units.tex import tex


class BaseFormatter(Formatter):

    SUBPLOT_ATTRIBUTES = {
        "domain": "domain",
        "crs": "crs_name",
    }

    STYLE_ATTRIBUTES = {
        "units": "units",
    }

    def convert_field(self, value, conversion):
        if conversion == "u":
            return str(value).upper()
        elif conversion == "l":
            return str(value).lower()
        return super().convert_field(value, conversion)

    def format_keys(self, format_string, kwargs):
        keys = (i[1] for i in self.parse(format_string) if i[1] is not None)
        for key in keys:
            kwargs[key] = self.format_key(key)
        return kwargs

    def format_key(self, key):
        return key

    def format(self, format_string, /, *args, **kwargs):
        kwargs = self.format_keys(format_string, kwargs)
        return super().format(format_string, *args, **kwargs)


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
    }
}


PRETTY_UNITS = {
    "celsius": "°C",
    "fahrenheit": "°F",
}


def default_label(data):
    if data.metadata("type") == "an":
        format_string = DEFAULT_ANALYSIS_TITLE
    else:
        format_string = DEFAULT_FORECAST_TITLE
    return format_string


def compare_units(unit_1, unit_2):
    from cf_units import Unit

    return Unit(unit_1) == Unit(unit_2)


def format_units(units):
    for name, formatted_units in PRETTY_UNITS.items():
        try:
            if compare_units(units, name):
                units = formatted_units
                break
        except ValueError:
            continue
    else:
        try:
            units = str(Unit(units))
        except ValueError:
            pass
    return f"${tex(units)}$"


def get_metadata(layer, attr):

    if attr in TIME_KEYS:
        handler = TimeHandler(layer.data.datetime())
        label = getattr(handler, attr)[0]

    else:
        candidates = [attr]
        if attr in MAGIC_KEYS:
            candidates = MAGIC_KEYS[attr]["preference"] + candidates

        for item in candidates:
            label = layer.data.metadata(item, default=None)
            if label is not None:
                break
        else:
            raise KeyError(f"No key {attr} found in metadata")

    return label


class TimeHandler:
    def __init__(self, times):
        if not isinstance(times, (list, tuple)):
            times = [times]
        for i, time in enumerate(times):
            if not isinstance(time, dict):
                times[i] = {"time": time}
        self.times = times

    def _extract_time(method):
        def wrapper(self):
            attr = method.__name__
            times = [self._named_time(time, attr) for time in self.times]
            _, indices = np.unique(times, return_index=True)
            return [times[i] for i in sorted(indices)]

        return property(wrapper)

    @staticmethod
    def _named_time(time, attr):
        return time.get(attr, time.get("time"))

    @property
    def time(self):
        return self.valid_time

    @_extract_time
    def base_time(self):
        pass

    @_extract_time
    def valid_time(self):
        pass

    @property
    def lead_time(self):
        if len(self.base_time) == 1 and len(self.valid_time) > 1:
            times = itertools.product(self.base_time, self.valid_time)
        elif len(self.base_time) == len(self.valid_time):
            times = zip(self.base_time, self.valid_time)
        else:
            times = [
                (
                    self._named_time(time, "base_time"),
                    self._named_time(time, "valid_time"),
                )
                for time in self.times
            ]
        return [int((vtime - btime).total_seconds() / 3600) for btime, vtime in times]


def list_to_human(iterable, conjunction="and", oxford_comma=False):
    """Convert a list to a human-readable string."""
    list_of_strs = [str(item) for item in iterable]

    if len(list_of_strs) > 2:
        list_of_strs = [", ".join(list_of_strs[:-1]), list_of_strs[-1]]
        if oxford_comma:
            list_of_strs[0] += ","

    return f" {conjunction} ".join(list_of_strs)
