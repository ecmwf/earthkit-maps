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

from earthkit.maps import metadata, utils


class BaseFormatter(Formatter):
    """
    Formatter of earthkit-maps components, enabling convient titles and labels.
    """

    #: Attributes of subplots which can be extracted by format strings
    SUBPLOT_ATTRIBUTES = {
        "domain": "domain_name",
        "crs": "crs_name",
    }

    #: Attributes of styles which can be extracted by format strings
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


class LayerFormatter(BaseFormatter):
    """
    Formatter of earthkit-maps `Layers`, enabling convient titles and labels.
    """

    def __init__(self, layer):
        self.layer = layer

    def format_keys(self, format_string, kwargs):
        keys = (i[1] for i in self.parse(format_string) if i[1] is not None)
        for key in keys:
            kwargs[key] = self.format_key(key)
        return kwargs

    def format_key(self, key):
        if key in self.SUBPLOT_ATTRIBUTES:
            value = getattr(self.layer.subplot, self.SUBPLOT_ATTRIBUTES[key])
        elif key in self.STYLE_ATTRIBUTES and self.layer.style is not None:
            value = getattr(self.layer.style, self.STYLE_ATTRIBUTES[key])
            if value is None:
                value = metadata.extract(self.layer.data, key)
                if key == "units":
                    value = metadata.units.format_units(value)
        else:
            value = metadata.extract(self.layer.data, key)
        return value


class SubplotFormatter(BaseFormatter):
    """
    Formatter of earthkit-maps `Subplots`, enabling convient titles and labels.
    """

    def __init__(self, subplot, unique=True):
        self.subplot = subplot
        self.unique = unique
        self._layer_index = None

    def convert_field(self, value, conversion):
        f = super().convert_field
        if isinstance(value, list):
            if isinstance(conversion, str) and conversion.isnumeric():
                return str(value[int(conversion)])
            return [f(v, conversion) for v in value]
        else:
            return f(value, conversion)

    def format_key(self, key):
        if key in self.SUBPLOT_ATTRIBUTES:
            values = [getattr(self.subplot, self.SUBPLOT_ATTRIBUTES[key])]
        else:
            values = [
                LayerFormatter(layer).format_key(key) for layer in self.subplot.layers
            ]
        return values

    def format_field(self, value, format_spec):
        f = super().format_field
        if isinstance(value, list):
            values = [f(v, format_spec) for v in value]
            if self._layer_index is not None:
                value = values[self._layer_index]
                self._layer_index = None
            else:
                if self.unique:
                    values = list(dict.fromkeys(values))
                value = utils.list_to_human(values)
        return value


class ChartFormatter(BaseFormatter):
    """
    Formatter of earthkit-maps `Charts`, enabling convient titles and labels.
    """

    def __init__(self, subplots, unique=True):
        self.subplots = subplots
        self.unique = unique
        self._layer_index = None

    def convert_field(self, value, conversion):
        f = super().convert_field
        if isinstance(value, list):
            if isinstance(conversion, str) and conversion.isnumeric():
                return str(value[int(conversion)])
            return [f(v, conversion) for v in value]
        else:
            return f(value, conversion)

    def format_key(self, key):
        values = [
            SubplotFormatter(subplot).format_key(key) for subplot in self.subplots
        ]
        values = [item for sublist in values for item in sublist]
        return values

    def format_field(self, value, format_spec):
        f = super().format_field
        if isinstance(value, list):
            values = [f(v, format_spec) for v in value]
            if self._layer_index is not None:
                value = values[self._layer_index]
                self._layer_index = None
            else:
                if self.unique:
                    values = list(dict.fromkeys(values))
                value = utils.list_to_human(values)
        return value


class TimeFormatter:
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


def format_month(data):
    import calendar

    month = data.metadata("month", default=None)
    if month is not None:
        month = calendar.month_name[month]
    else:
        time = data.datetime()
        if "valid_time" in time:
            time = time["valid_time"]
        else:
            time = time["base_time"]
        month = f"{time:%B}"
    return month
