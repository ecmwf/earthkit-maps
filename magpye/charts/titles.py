from string import Formatter

import emohawk
from pandas import Timestamp


NO_CFUNITS = False
try:
    from cf_units.tex import tex
except ImportError:
    NO_CFUNITS = True

METADATA = {
    "variable_name": {
        "preference": ["long_name", "standard_name", "short_name", "name"],
    }
}


UNCAPITALIZED = ["a", "is", "of", "the"]


class _DummyChart:
    def __init__(self, layer):
        self._layers = [layer]


class TitleFormatter(Formatter):

    TOP_LEVEL_KEYS = {
        "domain": "_domain",
    }

    def __init__(self, chart):
        super().__init__()
        self._chart = chart
        self._current_layer = None

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
            value = getattr(self._chart, self.TOP_LEVEL_KEYS[value])
        else:
            value = get_metadata(self._chart._layers, value, self._current_layer)
        if value == key:
            value = f"no_{value}".upper()
        f = super().format_field
        if isinstance(value, list):
            result = list_to_human(f(v, format_spec) for v in value)
        else:
            result = f(value, format_spec)
        self._current_layer = None
        return result


def get_metadata(layers, attr, layer=None):

    data_layers = [lyr.data for lyr in layers]
    if layer is not None:
        data_layers = [data_layers[layer]]

    labels = []
    for data in data_layers:

        data = emohawk.from_source("file", data).to_xarray()

        preference = [attr]
        if attr in METADATA:
            preference = METADATA[attr]["preference"] + preference

        try:
            data = data[list(data.data_vars)[0]]
        except AttributeError:
            pass

        for item in preference:
            try:
                label = getattr(data, item)
                break
            except AttributeError:
                continue
        else:
            label = attr

        try:
            label = label.values
        except AttributeError:
            pass
        else:
            try:
                if len(label) == 1:
                    label = label.item()
            except TypeError:
                pass
            label = Timestamp(label).to_pydatetime()

        if isinstance(label, str) and attr == "units" and not NO_CFUNITS:
            label = f"${tex(label)}$"

        labels.append(label)

    return labels


def format_string(self, label):
    if label is None:
        return _default_title(self)
    formatter = TitleFormatter(self)
    return formatter.format(label)


def title_string(string):
    working_string = string.replace("_", " ").title()
    chunks = working_string.split()
    for i in range(len(chunks)):
        if chunks[i].lower() in UNCAPITALIZED:
            chunks[i] = chunks[i].lower()
    chunks[0] = chunks[0].capitalize()
    return " ".join(chunks)


def _default_title(self):
    times = [emohawk.from_source("file", layer.data).to_datetime() for layer in self._layers]
    if len(set(times)) == 1:
        label = "{variable_name} at {time!0:%H:%M} on {time!0:%Y-%m-%d}"
    else:
        label = list_to_human(
            f"{{variable_name!{i}}} at {{time!{i}:%H:%M}} on {{time!{i}:%Y-%m-%d}}"
            for i in range(len(self._layers))
        )
    if self._domain is not None:
        label += " over {domain}"
    return format_string(self, label)


def colorbar_title(label, layer):
    chart = _DummyChart(layer)
    formatter = TitleFormatter(chart)

    if label is None:
        label = "{variable_name} ({units})"

    return formatter.format(label)


def list_to_human(iterable, conjunction="and", oxford_comma=False):
    """Convert a list to a human-readable string."""
    list_of_strs = [str(item) for item in iterable]

    if len(list_of_strs) > 2:
        list_of_strs = [", ".join(list_of_strs[:-1]), list_of_strs[-1]]
        if oxford_comma:
            list_of_strs[0] += ","

    return f" {conjunction} ".join(list_of_strs)
