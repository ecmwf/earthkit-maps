import itertools
from string import Formatter

import numpy as np

NO_CFUNITS = False
try:
    from cf_units.tex import tex
except ImportError:
    NO_CFUNITS = True


UNCAPITALIZED = ["a", "is", "of", "the"]


METADATA = {
    "variable_name": {
        "preference": ["long_name", "standard_name", "name", "short_name"],
    }
}

TIME_KEYS = ["base_time", "valid_time", "lead_time", "time"]


def default_title(self):
    if "valid_time" in self.layers[0].data.datetime():
        return _default_forecast_title(self)
    else:
        return _default_title(self)


def _default_forecast_title(self):
    label = (
        "{variable_name}\n"
        "Base time: {base_time:%H:%M} on {base_time:%Y-%m-%d}  "
        "Valid time: {valid_time:%H:%M} on {valid_time:%Y-%m-%d} (T+{lead_time})"
    )
    return format(self, label)


def _default_title(self):
    label = "{variable_name} at {valid_time:%H:%M} on {valid_time:%Y-%m-%d}"
    return format(self, label)


def list_to_human(iterable, conjunction="and", oxford_comma=False):
    """Convert a list to a human-readable string."""
    list_of_strs = [str(item) for item in iterable]

    if len(list_of_strs) > 2:
        list_of_strs = [", ".join(list_of_strs[:-1]), list_of_strs[-1]]
        if oxford_comma:
            list_of_strs[0] += ","

    return f" {conjunction} ".join(list_of_strs)


class SubplotFormatter(Formatter):

    TOP_LEVEL_KEYS = {
        "domain": "domain",
    }

    LAYER_KEYS = ["units"]

    def __init__(self, subplot):
        super().__init__()
        self._subplot = subplot
        self._current_layer = None

    @property
    def layers(self):
        return self._subplot.layers

    def format(self, format_string, /, *args, **kwargs):
        format_keys = [i[1] for i in self.parse(format_string) if i[1] is not None]
        for key in format_keys:
            if key not in kwargs:
                kwargs[key] = key
        return super().format(format_string, *args, **kwargs)

    def convert_field(self, value, conversion):
        if conversion is not None and conversion.isnumeric():
            self._current_layer = int(conversion)
            conversion = None
        return super().convert_field(value, conversion)

    def format_field(self, value, format_spec):
        key = value
        if value in self.TOP_LEVEL_KEYS:
            value = getattr(self._subplot, self.TOP_LEVEL_KEYS[value])
        elif value in self.LAYER_KEYS:
            value = getattr(self.layers[0], value)
        else:
            value = get_metadata(self.layers, value, self._current_layer)
        if value == key:
            value = f"no_{value}".upper()
        f = super().format_field

        if isinstance(value, list):
            if len(set(value)) == 1:
                result = f(value[0], format_spec)
            else:
                result = list_to_human(f(v, format_spec) for v in value)
        else:
            result = f(value, format_spec)
        self._current_layer = None
        return str(result)


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


def get_metadata(layers, attr, layer=None):

    if layer is not None:
        layers = [layers[layer]]

    labels = []
    for layer in layers:

        if attr == "time":
            label = layer.data.datetime()
        else:
            if not type(layer.data).__name__ == "GribField":
                label = "UNABLE TO READ METADATA"
            else:

                if attr in TIME_KEYS:
                    handler = TimeHandler(layer.data.datetime())
                    label = getattr(handler, attr)[0]

                else:
                    candidates = [attr]
                    if attr in METADATA:
                        candidates = METADATA[attr]["preference"] + candidates

                    for item in candidates:
                        label = layer.data.metadata(item, default=None)
                        if label is not None:
                            break
                    else:
                        label = f"<NO {attr.upper()}>"

        if isinstance(label, str) and attr == "units" and not NO_CFUNITS:
            label = f"${tex(label)}$"

        labels.append(label)

    return labels


def format(self, label=None):
    if label is None:
        return default_title(self)
    result = SubplotFormatter(self).format(label)
    return result
