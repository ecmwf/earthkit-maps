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

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import earthkit.data
import matplotlib.pyplot as plt

from earthkit.maps import domains
from earthkit.maps.domains import natural_earth
from earthkit.maps.layers import metadata
from earthkit.maps.layers.layers import Layer, LayerFormatter
from earthkit.maps.schemas import schema
from earthkit.maps.styles.auto import suggest_style


class SubplotFormatter(metadata.BaseFormatter):
    def __init__(self, subplot, unique=True):
        self.subplot = subplot
        self.unique = unique
        self._layer_index = None

    def convert_field(self, value, conversion):
        f = super().convert_field
        if isinstance(value, list):
            return [f(v, conversion) for v in value]
        else:
            return f(value, conversion)

    def format_key(self, key):
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
                value = metadata.list_to_human(values)
        return value


class Subplot:
    @classmethod
    def from_data(cls, superplot, data, *args, domain=None, crs=None, **kwargs):
        if not isinstance(data, earthkit.data.core.Base):
            data = earthkit.data.from_object(data)

        if domain is None and crs is None:
            try:
                crs = data.projection().to_cartopy_crs()
            except AttributeError:
                pass
        return cls(superplot, *args, domain=domain, crs=crs, **kwargs)

    def __init__(self, superplot, *args, domain=None, crs=None, **kwargs):
        self.domain = domains.parse(domain, crs)

        self.ax = superplot.fig.add_subplot(*args, projection=self.domain.crs, **kwargs)

        if self.domain.bounds is not None:
            self.ax.set_extent(self.domain.bounds, crs=self.domain.crs)

        self.superplot = superplot
        self.layers = []

    @property
    def fig(self):
        return self.superplot.fig

    @property
    def distinct_legend_layers(self):
        """Group layers by style."""
        legend_layers = []
        for layer in self.layers:
            for legend_layer in legend_layers:
                if legend_layer.style == layer.style:
                    break
            else:
                legend_layers.append(layer)
        return legend_layers

    def gridded_scalar(method):
        def wrapper(self, data, x=None, y=None, transform=None, style=None, **kwargs):
            # - TEMPORARY: in the future all "fields" will be "fieldlists" -
            if isinstance(data, earthkit.data.core.Base):
                try:
                    data = data[0]
                except (ValueError, TypeError):
                    pass
            # --------------------------------------------------------------

            if x is not None and y is not None:
                if transform is None:
                    raise ValueError(
                        "you must pass a 'transform' when plotting manually "
                        "with x and y coordinates"
                    )
                values = data
            else:
                if not isinstance(data, earthkit.data.core.Base):
                    data = earthkit.data.from_object(data)
                x, y, values = extract_scalar(data, self.domain)
                if transform is None:
                    transform = data.projection().to_cartopy_crs()

            try:
                source_units = data.metadata("units")
            except AttributeError:
                source_units = None

            if style is None:
                style_units = kwargs.pop("units", source_units)
                style = suggest_style(data, units=style_units)

            values = style.convert_units(values, source_units)

            if "transform_first" not in kwargs:
                kwargs["transform_first"] = self._can_transform_first(method)

            mappable = method(
                self, x, y, values, style=style, transform=transform, **kwargs
            )

            layer = Layer(data, mappable, self, style=style)
            self.layers.append(layer)

            return layer

        return wrapper

    def _can_transform_first(self, method):
        if self.domain._can_transform_first and method.__name__ != "pcolormesh":
            return True
        else:
            return False

    @gridded_scalar
    def plot(self, *args, style=None, **kwargs):
        try:
            return style.plot(self.ax, *args, **kwargs)
        except NotImplementedError:
            return style.contourf(self.ax, *args, **kwargs)

    @gridded_scalar
    def contourf(self, *args, style=None, **kwargs):
        return style.contourf(self.ax, *args, **kwargs)

    @gridded_scalar
    def contour(self, *args, style=None, **kwargs):
        return style.contour(self.ax, *args, **kwargs)

    shaded_contour = contourf

    @gridded_scalar
    def pcolormesh(self, *args, style=None, **kwargs):
        return style.pcolormesh(self.ax, *args, **kwargs)

    @gridded_scalar
    def scatter(self, *args, style=None, **kwargs):
        return style.scatter(self.ax, *args, **kwargs)

    @schema.coastlines.apply()
    def coastlines(self, *args, resolution="auto", **kwargs):
        """Add coastal outlines from the Natural Earth “coastline” collection.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = natural_earth.RESOLUTIONS.get(resolution, resolution)
        return self.ax.coastlines(*args, resolution=resolution, **kwargs)

    @schema.borders.apply()
    def borders(
        self, *args, resolution="auto", labels=False, label_kwargs=None, **kwargs
    ):
        """Add country boundary polygons from Natural Earth.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = natural_earth.RESOLUTIONS.get(resolution, resolution)
        if resolution == "auto":
            feature = cfeature.BORDERS
        else:
            feature = cfeature.NaturalEarthFeature(
                "cultural", "admin_0_countries", resolution
            )
        if labels:
            label_kwargs = label_kwargs or dict()
            label_kwargs = {
                **dict(
                    ha="center",
                    va="center",
                    bbox=dict(
                        boxstyle="round",
                        ec=(0.2, 0.2, 0.2, 0),
                        fc=(0.3, 0.3, 0.3),
                    ),
                    fontsize=8,
                    weight="bold",
                    color=(0.95, 0.95, 0.95),
                    clip_on=True,
                    clip_box=self.ax.bbox,
                    transform=ccrs.Geodetic(),
                ),
                **label_kwargs,
            }

            label_key = labels if isinstance(labels, str) else "ISO_A2_EH"

            resolution = "110m" if resolution == "auto" else resolution
            shpfilename = shpreader.natural_earth(
                resolution=resolution, category="cultural", name="admin_0_countries"
            )
            reader = shpreader.Reader(shpfilename)
            for record in reader.records():
                name = record.attributes[label_key]
                x = record.attributes["LABEL_X"]
                y = record.attributes["LABEL_Y"]
                self.ax.text(x, y, name, **label_kwargs)
        return self.ax.add_feature(feature, *args, **kwargs)

    @schema.land.apply()
    def land(self, *args, resolution="auto", **kwargs):
        """Add land polygons from the Natural Earth collection.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = natural_earth.RESOLUTIONS.get(resolution, resolution)
        if resolution == "auto":
            feature = cfeature.LAND
        else:
            feature = cfeature.NaturalEarthFeature("physical", "land", resolution)
        return self.ax.add_feature(feature, *args, **kwargs)

    @schema.land.apply()
    def ocean(self, *args, resolution="auto", **kwargs):
        """Add ocean polygons from the Natural Earth collection.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = natural_earth.RESOLUTIONS.get(resolution, resolution)
        if resolution == "auto":
            feature = cfeature.OCEAN
        else:
            feature = cfeature.NaturalEarthFeature("physical", "land", resolution)
        return self.ax.add_feature(feature, *args, **kwargs)

    def stock_img(self, *args, **kwargs):
        self.ax.stock_img(*args, **kwargs)

    @schema.gridlines.apply()
    def gridlines(self, *args, **kwargs):
        """Add gridlines to the map."""
        self._gridlines = self.ax.gridlines(*args, **kwargs)
        return self._gridlines

    @schema.legend.apply()
    def legend(self, *args, **kwargs):
        legends = []
        for layer in self.distinct_legend_layers:
            if layer.style is not None:
                legend = layer.style.legend(
                    self.fig,
                    layer,
                    *args,
                    ax=layer.axes,
                    **kwargs,
                )
            legends.append(legend)
        return legends

    @property
    def _default_title_template(self):
        templates = [layer._default_title_template for layer in self.layers]
        if len(set(templates)) == 1:
            template = templates[0]
        else:
            title_parts = []
            for i, template in enumerate(templates):
                keys = [k for _, k, _, _ in SubplotFormatter().parse(template)]
                for key in set(keys):
                    template = template.replace("{" + key, "{" + key + f"!{i}")
                title_parts.append(template)
            template = metadata.list_to_human(title_parts)
        return template

    @schema.title.apply()
    def title(self, label=None, unique=True, wrap=True, **kwargs):
        if label is None:
            label = self._default_title_template
        label = self.format_string(label, unique)
        plt.sca(self.ax)
        return plt.title(label, wrap=wrap, **kwargs)

    def format_string(self, string, unique=True):
        return SubplotFormatter(self, unique=unique).format(string)


def extract_scalar(data, domain):
    try:
        data = data[0]
    except (ValueError, TypeError):
        data = data

    values, points = domain.bbox(data)

    y = points["y"]
    x = points["x"]
    # if data.projection().CF_GRID_MAPPING_NAME == "latitude_longitude":
    #     x[x > 180] -= 360

    return x, y, values


def extract_vector(data, domain):
    x, y, u_values = extract_scalar(data[0], domain)
    _, _, v_values = extract_scalar(data[1], domain)
    return x, y, (u_values, v_values)
