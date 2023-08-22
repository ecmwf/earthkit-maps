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

from earthkit.maps.layers import metadata


class LayerFormatter(metadata.BaseFormatter):
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
                value = metadata.get_metadata(self.layer, key)
                if key == "units":
                    value = metadata.format_units(value)
        else:
            value = metadata.get_metadata(self.layer, key)
        return value


class Layer:
    def __init__(self, data, mappable, subplot, style=None):
        self.data = data
        self.mappable = mappable
        self.subplot = subplot
        self.style = style

    @property
    def fig(self):
        return self.subplot.fig

    def legend(self, *args, **kwargs):
        if self.style is not None:
            return self.style.legend(
                self.fig,
                self,
                *args,
                ax=self.axes,
                **kwargs,
            )

    @property
    def ax(self):
        return self.subplot.ax

    @property
    def axes(self):
        return [self.ax]

    def format_string(self, string):
        return LayerFormatter(self).format(string)

    @property
    def _default_title_template(self):
        if self.data.metadata("type") == "an":
            template = metadata.DEFAULT_ANALYSIS_TITLE
        else:
            template = metadata.DEFAULT_FORECAST_TITLE
        return template


class MultiplotLayer:
    def __init__(self, layers):
        self.layers = layers

    @property
    def subplots(self):
        return [layer.subplot for layer in self.layers]

    @property
    def fig(self):
        return self.subplots[0].fig

    @property
    def axes(self):
        return [subplot.ax for subplot in self.subplots]

    @property
    def style(self):
        return self.layers[0].style

    def legend(self, *args, **kwargs):
        if self.style is not None:
            return self.style.legend(
                self.fig,
                self,
                *args,
                ax=self.axes,
                **kwargs,
            )

    @property
    def mappable(self):
        return self.layers[0].mappable

    def format_string(self, string, unique=True):
        results = [layer.format_string(string) for layer in self.layers]

        if unique:
            results = list(dict.fromkeys(results))

        result = metadata.list_to_human(results)
        return result
