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

import cartopy.feature as cfeature
import earthkit.data
import matplotlib.pyplot as plt

from earthkit.maps import domains, inputs, utils
from earthkit.maps.charts.layers import Layer
from earthkit.maps.domains import natural_earth
from earthkit.maps.metadata.formatters import LayerFormatter, SubplotFormatter
from earthkit.maps.schemas import schema


class Subplot:
    """
    An individual set of axes onto which one or more layer can be plotted.
    """

    @classmethod
    def from_data(cls, chart, data, *args, domain=None, crs=None, **kwargs):
        if not isinstance(data, earthkit.data.core.Base):
            data = earthkit.data.from_object(data)

        if domain is None and crs is None:
            try:
                crs = data.projection().to_cartopy_crs()
            except AttributeError:
                pass
        return cls(chart, *args, domain=domain, crs=crs, **kwargs)

    def __init__(self, chart, *args, domain=None, crs=None, **kwargs):
        self.domain = domains.parse(domain, crs)

        self.ax = chart.fig.add_subplot(*args, projection=self.domain.crs, **kwargs)

        if self.domain.bounds is not None:
            self.ax.set_extent(self.domain.bounds, crs=self.domain.crs)

        self.chart = chart
        self.layers = []

    @property
    def fig(self):
        return self.chart.fig

    @property
    def crs_name(self):
        return self.domain.crs.__class__.__name__

    @property
    def domain_name(self):
        name = self.domain.title
        if name == "None":
            if self.domain.crs.__class__.__name__ == "PlateCarree":
                extent = self.ax.get_extent()
                if extent == (-180.0, 180.0, -90.0, 90.0):
                    name = "Global"
                else:
                    name = domains.bounds.to_string(extent)
        return name

    @property
    def distinct_legend_layers(self):
        """Layers on this subplot which have a unique `Style`."""
        unique_layers = []
        for layer in self.layers:
            for legend_layer in unique_layers:
                if legend_layer.style == layer.style:
                    break
            else:
                unique_layers.append(layer)
        return unique_layers

    def _can_transform_first(self, method):
        """
        Check if the data can be transformed onto the target projection.

        Some matplotlib methods can be sped up by transforming data coordinates
        before plotting, but this is not compatible with all projections nor all
        plotting methods. This method checks if a given domain and method is
        compatible with `transform_first`.

        Parameters
        ----------
        method : method
            The class method to check for compatibility with `transform_first`.

        Returns
        -------
        bool
        """
        if self.domain._can_transform_first and method.__name__ != "pcolormesh":
            return True
        else:
            return False

    def plot_gridded_scalar(method):
        """
        Decorator for transforming input data into plottable components.

        Parameters
        ----------
        method : method
            The method for which to transform input parameters to plottable
            components.
        """

        def wrapper(self, data, *args, transform_first=None, style=None, **kwargs):
            input_data = inputs.Input(
                data, *args, domain=self.domain, style=style, **kwargs
            )

            kwargs.pop("x", None)
            kwargs.pop("y", None)
            kwargs.pop("units", None)

            if transform_first is None:
                transform_first = self._can_transform_first(method)

            mappable = method(
                self,
                input_data.x,
                input_data.y,
                input_data.values,
                style=input_data.style,
                transform=input_data.transform,
                transform_first=transform_first,
                **kwargs,
            )

            layer = Layer(data, mappable, self, style=input_data.style)
            self.layers.append(layer)
            return layer

        return wrapper

    def plot(self, data, *args, **kwargs):
        if data.__class__.__name__ in ("DataFrame", "Series"):
            raise NotImplementedError(
                "Plotting pandas DataFrames and Series is an upcoming feature"
            )
        else:
            return self._plot_gridded_scalar(data, *args, **kwargs)

    @plot_gridded_scalar
    def _plot_gridded_scalar(self, *args, style=None, **kwargs):
        try:
            return style.plot(self.ax, *args, **kwargs)
        except NotImplementedError:
            return style.contourf(self.ax, *args, **kwargs)

    @plot_gridded_scalar
    def contourf(self, *args, style=None, **kwargs):
        return style.contourf(self.ax, *args, **kwargs)

    shaded_contour = contourf  # alias to contourf

    @plot_gridded_scalar
    def contour(self, *args, style=None, **kwargs):
        return style.contour(self.ax, *args, **kwargs)

    @plot_gridded_scalar
    def pcolormesh(self, *args, style=None, **kwargs):
        return style.pcolormesh(self.ax, *args, **kwargs)

    @plot_gridded_scalar
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
        if "color" in kwargs:
            kwargs["edgecolor"] = kwargs.pop("color")
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
            feature = cfeature.NaturalEarthFeature("physical", "ocean", resolution)
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
                legend = layer.style.legend(layer, *args, **kwargs)
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
            template = utils.list_to_human(title_parts)
        return template

    @schema.title.apply()
    def title(self, label=None, unique=True, wrap=True, **kwargs):
        if label is None:
            label = self._default_title_template
        label = self.format_string(label, unique)
        plt.sca(self.ax)
        return plt.title(label, wrap=wrap, **kwargs)

    def format_string(self, string, unique=True, grouped=True):
        if not grouped:
            return utils.list_to_human(
                [LayerFormatter(layer).format(string) for layer in self.layers]
            )
        else:
            return SubplotFormatter(self, unique=unique).format(string)
