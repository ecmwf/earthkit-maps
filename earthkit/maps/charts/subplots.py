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

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import earthkit.data
import matplotlib.pyplot as plt
from adjustText import adjust_text

from earthkit.maps import domains, inputs, utils
from earthkit.maps.charts.layers import Layer
from earthkit.maps.domains import natural_earth
from earthkit.maps.metadata import components
from earthkit.maps.metadata.formatters import LayerFormatter, SubplotFormatter
from earthkit.maps.schemas import schema
from earthkit.maps.styles.levels import step_range


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

    def __init__(self, chart, *args, domain=None, domain_crs=None, crs=None, **kwargs):
        if isinstance(domain, domains.Domain):
            self.domain = domain
            domain_crs = domain.crs
        else:
            self.domain = domains.parse(domain, crs)

        self.ax = chart.fig.add_subplot(*args, projection=self.domain.crs, **kwargs)

        if self.domain.bounds is not None:
            self.ax.set_extent(self.domain.bounds, crs=domain_crs or self.domain.crs)

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
            data = inputs.sanitise(data)

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

    def plot_gridded_vector(method):
        """
        Decorator for transforming input data into plottable components.

        Parameters
        ----------
        method : method
            The method for which to transform input parameters to plottable
            components.
        """

        def wrapper(self, data, transform_first=None, style=None, **kwargs):
            if len(data) == 2:
                u, v = data
            else:
                u, v = components.extract(*data, "uv")

            u = inputs.sanitise(u)
            v = inputs.sanitise(v)

            input_data = inputs.Vector(u, v, domain=self.domain, style=style, **kwargs)

            kwargs.pop("x", None)
            kwargs.pop("y", None)
            kwargs.pop("units", None)

            if transform_first is None:
                transform_first = self._can_transform_first(method)

            mappable = method(
                self,
                input_data.x,
                input_data.y,
                input_data.u,
                input_data.v,
                style=input_data.style,
                transform=input_data.transform,
                **kwargs,
            )

            layer = Layer([u, v], mappable, self, style=input_data.style)
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

    @plot_gridded_vector
    @schema.barbs.apply()
    def barbs(self, *args, style=None, **kwargs):
        style.barbs(self.ax, *args, **kwargs)

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
            resolution = "110m" if resolution == "auto" else resolution
            shpfilename = shpreader.natural_earth(
                resolution=resolution, category="cultural", name="admin_0_countries"
            )
            reader = shpreader.Reader(shpfilename)
            if not isinstance(labels, str):
                labels = "ISO_A2_EH"
            self._add_polygon_labels(
                reader, x_key="LABEL_X", y_key="LABEL_Y", label_key=labels
            )

        if "color" in kwargs:
            kwargs["edgecolor"] = kwargs.pop("color")
        return self.ax.add_feature(feature, *args, **kwargs)

    @schema.shapes.apply()
    def shapes(
        self,
        shapes,
        *args,
        transform=ccrs.PlateCarree(),
        adjust_labels=False,
        labels=False,
        **kwargs,
    ):
        if isinstance(shapes, str):
            shapes = shpreader.Reader(shapes)
        results = self.ax.add_geometries(
            shapes.geometries(), transform, *args, **kwargs
        )
        if labels:
            label_key = labels if isinstance(labels, str) else None
            self._add_polygon_labels(
                shapes, label_key=label_key, adjust_labels=adjust_labels
            )
        return results

    def _add_polygon_labels(
        self, reader, x_key=None, y_key=None, adjust_labels=False, label_key=None
    ):
        records = list(reader.records())
        label_kwargs = dict()
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

        if label_key is None:
            for label_key in records[0].attributes:
                if "name" in label_key.lower():
                    break

        texts = []
        for record in reader.records():
            name = record.attributes[label_key]

            if record.geometry.__class__.__name__ == "MultiPolygon":
                centroid = max(record.geometry.geoms, key=lambda a: a.area).centroid
            else:
                centroid = record.geometry.centroid
            x = centroid.x
            y = centroid.y
            if x_key:
                x = record.attributes[x_key]
            if y_key:
                y = record.attributes[y_key]

            text = self.ax.text(x, y, name, **label_kwargs)
            texts.append(text)
        if adjust_labels:
            adjust_text(texts)
        return texts

    @schema.states_provinces.apply()
    def states_provinces(
        self, *args, resolution="auto", labels=False, adjust_labels=False, **kwargs
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
            feature = cfeature.STATES
        else:
            feature = cfeature.NaturalEarthFeature(
                "cultural",
                "admin_1_states_provinces",
                resolution,
                facecolor="none",
            )

        if labels:
            resolution = "110m" if resolution == "auto" else resolution
            shpfilename = shpreader.natural_earth(
                resolution=resolution,
                category="cultural",
                name="admin_1_states_provinces",
            )
            reader = shpreader.Reader(shpfilename)
            if not isinstance(labels, str):
                labels = "name"
            self._add_polygon_labels(
                reader, label_key=labels, adjust_labels=adjust_labels
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

    @schema.ocean.apply()
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

    @schema.rivers.apply()
    def rivers(self, *args, resolution="auto", **kwargs):
        """Add ocean polygons from the Natural Earth collection.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = natural_earth.RESOLUTIONS.get(resolution, resolution)
        if resolution == "auto":
            feature = cfeature.RIVERS
        else:
            feature = cfeature.NaturalEarthFeature(
                "physical",
                "rivers_lake_centerlines",
                resolution,
                facecolor="none",
                edgecolor=kwargs.pop("edgecolor", "#C3EDFF"),
            )
        return self.ax.add_feature(feature, *args, **kwargs)

    @schema.urban_areas.apply()
    def urban_areas(self, *args, resolution="50m", **kwargs):
        """Add urban area polygons from the Natural Earth collection.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = natural_earth.RESOLUTIONS.get(resolution, resolution)
        feature = cfeature.NaturalEarthFeature("cultural", "urban_areas", resolution)
        return self.ax.add_feature(feature, *args, **kwargs)

    @schema.lakes.apply()
    def lakes(self, *args, resolution="50m", **kwargs):
        """Add lake polygons from the Natural Earth collection.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = natural_earth.RESOLUTIONS.get(resolution, resolution)
        if resolution == "auto":
            feature = cfeature.LAKES
        else:
            feature = cfeature.NaturalEarthFeature("physical", "lakes", resolution)
        return self.ax.add_feature(feature, *args, **kwargs)

    def cities(
        self,
        *args,
        density="medium",
        color="black",
        capitals_only=False,
        adjust_labels=True,
        **kwargs,
    ):
        density = natural_earth.RESOLUTIONS.get(density, density)
        fname = shpreader.natural_earth(
            resolution=density,
            category="cultural",
            name="populated_places",
        )
        reader = shpreader.Reader(fname)
        records = list(reader.records())

        texts = []
        for record in records:
            if capitals_only and not record.attributes["ADM0CAP"]:
                continue
            if self.domain.contains_point(
                (record.geometry.x, record.geometry.y),
                crs=ccrs.PlateCarree(),
            ):
                scatter_kwargs = {
                    "marker": "o",
                    "s": 10,
                    "color": "red",
                    "edgecolor": "black",
                    "linewidths": 0.5,
                }
                text_kwargs = {
                    "fontsize": 7,
                    "color": color,
                }
                if record.attributes["ADM0CAP"]:
                    scatter_kwargs = {
                        "marker": "s",
                        "s": 25,
                        "color": "goldenrod",
                        "edgecolor": "black",
                        "linewidths": 0.5,
                    }
                    text_kwargs = {
                        "fontsize": 8,
                        "fontweight": "bold",
                        "color": color,
                    }
                elif record.attributes["RANK_MAX"] < 8:
                    scatter_kwargs = {
                        "marker": "o",
                        "s": 6,
                        "color": "navy",
                    }
                    text_kwargs = {
                        "fontsize": 7,
                        "fontstyle": "italic",
                        "color": color,
                    }
                self.ax.scatter(
                    record.geometry.x,
                    record.geometry.y,
                    transform=ccrs.PlateCarree(),
                    zorder=10,
                    **scatter_kwargs,
                )
                text = self.ax.text(
                    record.geometry.x,
                    record.geometry.y,
                    record.attributes["NAME_EN"],
                    transform=ccrs.PlateCarree(),
                    clip_on=True,
                    zorder=10,
                    **text_kwargs,
                )
                texts.append(text)
        if adjust_labels:
            warnings.warn(
                "City label positions are being automatically adjusted to "
                "minimise overlaps, which can take a long time. This behaviour "
                "can be switched off by passing `adjust_labels=False`."
            )
            adjust_text(texts)
        return texts

    def image(self, img, extent, origin="upper", transform=None):
        if isinstance(img, str):
            import PIL

            img = PIL.Image.open(img)
        if transform is None:
            transform = ccrs.PlateCarree()
        return self.ax.imshow(img, origin=origin, extent=extent, transform=transform)

    def stock_img(self, *args, **kwargs):
        self.ax.stock_img(*args, **kwargs)

    @schema.gridlines.apply()
    def gridlines(self, *args, xstep=None, xref=0, ystep=None, yref=0, **kwargs):
        """
        Add gridlines to the subplot.

        Parameters
        ----------
        xstep : float, optional
            The step/difference between each x gridline.
        xref : float, optional
            The reference point around which to calibrate the x level range.
        ystep : float, optional
            The step/difference between each y gridline.
        yref : float, optional
            The reference point around which to calibrate the y level range.

        Note
        ----
            Any keyword arguments accepted by cartopy's `gridlines` method can
            be used when adding gridlines.
        """
        if xstep is not None:
            kwargs["xlocs"] = step_range([-180, 180], xstep, xref)
        if ystep is not None:
            kwargs["ylocs"] = step_range([-90, 90], ystep, yref)
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
