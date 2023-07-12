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
import cf_units
import matplotlib.pyplot as plt

from earthkit.maps import domains, legends, metadata, styles

NE_RESOLUTIONS = {
    "low": "110m",
    "medium": "50m",
    "high": "10m",
}


def compare_units(unit_1, unit_2):
    from cf_units import Unit

    return Unit(unit_1) == Unit(unit_2)


class Layer:
    def __init__(self, data, layer, chart, units=None, legend=True):
        self.data = data
        self.layer = layer
        self._chart = chart
        self._units = units
        self._legend = legend

    @property
    def units(self):
        from cf_units import Unit
        from cf_units.tex import tex

        if self._units is None:
            self._units = self.data.metadata("units")
        for name, unit in metadata.labels.PRETTY_UNITS.items():
            if compare_units(self._units, name):
                break
        else:
            unit = Unit(self._units).symbol

        try:
            latex = f"${tex(unit)}$"
        except (SyntaxError, ValueError):
            try:
                latex = f"${tex(unit.replace('.', ' '))}$"
            except (SyntaxError, ValueError):
                latex = unit

        return latex


class Subplot:
    @classmethod
    def from_data(cls, chart, data, *args, **kwargs):
        crs = kwargs.pop("crs", chart.domain.crs)
        if crs is None:
            crs = data.projection().to_cartopy()
        return cls(chart, *args, crs=crs, **kwargs)

    def __init__(self, chart, *args, domain=None, crs=None, **kwargs):
        if all((domain is None, crs is None, chart.domain.crs is not None)):
            self.domain = chart.domain
        else:
            self.domain = domains.parse_domain(domain, crs)
        self.ax = chart.fig.add_subplot(*args, projection=self.domain.crs, **kwargs)
        if self.domain.bounds is not None:
            self.ax.set_extent(self.domain.bounds, crs=self.domain.crs)

        self._chart = chart
        self.layers = []
        self._queue = []

        self._title = None
        self._gridlines = None

    @property
    def crs_name(self):
        return self.domain.crs.__class__.__name__

    @property
    def _default_fontsize(self):
        font_sizes = {
            1: 13,
            2: 13,
            3: 12,
            4: 11,
            5: 11,
            6: 10,
            7: 9,
        }
        return font_sizes.get(self._chart.rows, 8)

    def _release_queue(self):
        while len(self._queue):
            method, args, kwargs = self._queue.pop(0)
            method(self, *args, **kwargs)

    def _extract(self, data):
        values, points = self.domain.bbox(data)

        y = points["y"]
        x = points["x"]
        if data.projection().CF_GRID_MAPPING_NAME == "latitude_longitude":
            x[x > 180] -= 360

        return x, y, values

    def add_layer(self, method, vector=False):
        def wrapper(
            data, *args, units=None, legend=True, transform=None, style=None, **kwargs
        ):
            v_field = None
            if vector:
                _, _, v_field = self._extract(data[1])

            try:
                field = data[0]
            except (ValueError, TypeError):
                field = data

            x, y, values = self._extract(field)
            if units is not None:
                values = cf_units.Unit(data.metadata("units")).convert(values, units)

            if transform is None:
                transform = (field).projection().to_cartopy_crs()

            values = (values,)
            if v_field is not None:
                values = (values, v_field)

            if style is not None:
                kwargs = {**kwargs, **style.to_kwargs(data, method)}

            layer = method(x, y, *values, *args, transform=transform, **kwargs)

            self.layers.append(
                Layer(data, layer, self._chart, units=units, legend=legend)
            )

            return layer

        return wrapper

    def await_crs(method):
        def wrapper(self, *args, **kwargs):
            if self.domain is None:
                self._queue.append((method, args, kwargs))
            else:
                return method(self, *args, **kwargs)

        return wrapper

    def distinct_layers(self):
        if not self.layers:
            return []

        layers = [self.layers[0]]
        for new_layer in self.layers[1:]:
            for layer in layers:
                if all(
                    (
                        layer.layer.cmap == new_layer.layer.cmap,
                        list(layer.layer.levels) == list(new_layer.layer.levels),
                        # metadata.variable(layer.data)==metadata.variable(new_layer.data),
                    )
                ):
                    break
            else:
                layers.append(new_layer)
        return layers

    @property
    def _transform_first(self):
        """Identify if this subplot supports `transform_first` arguments.

        In order to speed up plotting of reprojected fields, we can pass the
        argument `transform_first` to cartopy's `contour` and `contourf`
        functions. This means that the reprojection of data is applied
        mathematically before the data is passed to the plot, as opposed to
        generating an image in the data's native projection and then
        reprojecting the image - which typically takes significantly longer.

        However, this functionality can produce unexpected results when used
        with certain projections. This attribute identifies whether or not this
        subplot's projection is suitable for passing `transform_first=True`.
        """
        return self.domain.crs.__class__.__name__ not in (
            "NearsidePerspective",
            "NorthPolarStereo",
            "SouthPolarStereo",
        )

    @await_crs
    def coastlines(self, *args, resolution="auto", **kwargs):
        """Add coastal outlines from the Natural Earth “coastline” collection.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = NE_RESOLUTIONS.get(resolution, resolution)
        return self.ax.coastlines(*args, resolution=resolution, **kwargs)

    @await_crs
    def borders(self, *args, resolution="auto", **kwargs):
        """Add country boundary polygons from Natural Earth.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = NE_RESOLUTIONS.get(resolution, resolution)
        if resolution == "auto":
            feature = cfeature.BORDERS
        else:
            feature = cfeature.NaturalEarthFeature(
                "cultural", "admin_0_countries", resolution
            )
        return self.ax.add_feature(feature, *args, **kwargs)

    @await_crs
    def gridlines(self, *args, **kwargs):
        """Add gridlines to the map."""
        self._gridlines = self.ax.gridlines(*args, **kwargs)
        return self._gridlines

    @await_crs
    def ocean(self, *args, resolution="auto", **kwargs):
        """Add ocean polygons from the Natural Earth collection.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = NE_RESOLUTIONS.get(resolution, resolution)
        if resolution == "auto":
            feature = cfeature.OCEAN
        else:
            feature = cfeature.NaturalEarthFeature("physical", "ocean", resolution)
        return self.ax.add_feature(feature, *args, **kwargs)

    @await_crs
    def land(self, *args, resolution="auto", **kwargs):
        """Add land polygons from the Natural Earth collection.

        Parameters
        ----------
        resolution: (str, optional)
            One of "low", "medium" or "high", or a named resolution from the
            Natrual Earth dataset.
        """
        resolution = NE_RESOLUTIONS.get(resolution, resolution)
        if resolution == "auto":
            feature = cfeature.LAND
        else:
            feature = cfeature.NaturalEarthFeature("physical", "land", resolution)
        return self.ax.add_feature(feature, *args, **kwargs)

    @await_crs
    def stock_img(self, *args, **kwargs):
        return self.ax.stock_img(*args, **kwargs)

    # @schema.apply("cmap")
    def contourf(self, *args, transform_first=None, **kwargs):

        if "colors" in kwargs:
            kwargs["colors"] = styles.parse_colors(kwargs["colors"])
        if transform_first is None:
            transform_first = self._transform_first
        return self.add_layer(self.ax.contourf)(
            *args, transform_first=transform_first, **kwargs
        )

    def pcolormesh(self, *args, **kwargs):
        return self.add_layer(self.ax.pcolormesh)(*args, **kwargs)

    def contour(
        self,
        *args,
        transform_first=None,
        legend=False,
        labels=True,
        label_fontsize=7,
        label_colors=None,
        label_frequency=1,
        label_background=None,
        label_fmt=None,
        **kwargs,
    ):
        if transform_first is None:
            transform_first = self._transform_first
        contours = self.add_layer(self.ax.contour)(
            *args, transform_first=transform_first, legend=legend, **kwargs
        )

        if labels:
            clabels = self.ax.clabel(
                contours,
                contours.levels[0::label_frequency],
                inline=True,
                fontsize=label_fontsize,
                colors=label_colors,
                fmt=label_fmt,
                inline_spacing=2,
            )
            if label_background is not None:
                for label in clabels:
                    label.set_backgroundcolor(label_background)

        return contours

    def title(self, label=None, **kwargs):
        label = metadata.labels.title_from_subplot(self, label)
        kwargs["fontsize"] = kwargs.pop("fontsize", self._default_fontsize)
        plt.sca(self.ax)
        self._title = plt.title(label, **kwargs)
        return self._title


class Subplots:
    def __init__(self, chart):
        self._subplots = []
        self._chart = chart

        self._legends = []

    @property
    def domain(self):
        domains = [subplot.domain for subplot in self]
        if len(domains) > 1:
            if all([str(domain) == str(domains[0]) for domain in domains]):
                domains = domains[0]
        return domains

    @property
    def subplots(self):
        if not self._subplots:
            self._chart.add_subplot()
        return self._subplots

    def __getattr__(self, attr):
        try:
            methods = [getattr(subplot, attr) for subplot in self.subplots]
        except AttributeError:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{attr}'")

        return lambda *args, **kwargs: [m(*args, **kwargs) for m in methods]

    def __len__(self):
        return len(self._subplots)

    def __getitem__(self, i):
        return self._subplots[i]

    def add_subplot(self, subplot):
        self._subplots.append(subplot)

    def distinct_layers(self):
        layers = self.subplots[0].distinct_layers()

        for subplot in self.subplots[1:]:
            for layer in layers:
                for new_layer in subplot.distinct_layers():
                    if all(
                        (
                            layer.layer.cmap == new_layer.layer.cmap,
                            list(layer.layer.levels) == list(new_layer.layer.levels),
                            # metadata.variable(layer.data)==metadata.variable(new_layer.data),
                        )
                    ):
                        break
                else:
                    layers.append(new_layer)
        return layers

    def _resize_legends(self):
        positions = [subplot.ax.get_position() for subplot in self.subplots]
        x0 = min(pos.x0 for pos in positions)
        x1 = max(pos.x1 for pos in positions)
        y0 = min(pos.y0 for pos in positions)
        y1 = max(pos.y1 for pos in positions)
        width = x1 - x0
        height = y1 - y0

        offset = {"right": 0, "left": 0, "bottom": 0.02, "top": 0}

        gridlines = self[0]._gridlines
        if gridlines:
            pad = {"right": 0.045, "left": 0.045, "bottom": 0.02, "top": 0.02}
            for side in offset:
                if getattr(gridlines, f"{side}_labels"):
                    offset[side] += pad[side]

        for legend in self._legends:
            if not getattr(legend, "auto", False):
                continue
            position = {
                "right": [
                    x0 + width + 0.01 + offset["right"],
                    y0,
                    0.03,
                    height,
                ],
                "left": [x0 - 0.06 - offset["left"], y0, 0.03, height],
                "bottom": [x0, y0 - 0.04 - offset["bottom"], width, 0.03],
                "top": [x0, y0 + height + 0.04 + offset["top"], width, 0.03],
            }[legend.location]
            offset[legend.location] += 0.1
            legend.ax.set_position(position)

    def legend(self, *args, orientation=None, location=None, ticks=None, **kwargs):
        layers = self.distinct_layers()
        layers = [layer for layer in layers if layer._legend]

        if not isinstance(orientation, (list, tuple)):
            orientation = [orientation] * len(layers)
        if not isinstance(location, (list, tuple)):
            location = [location] * len(layers)

        for layer, orientation, location in zip(layers, orientation, location):
            legend = legends.colorbar(
                layer, *args, orientation=orientation, location=location, **kwargs
            )
            if ticks is not None:
                legend.set_ticks(ticks)
            self._legends.append(legend)

    def contourf(self, data, *args, **kwargs):
        if not hasattr(data, "__len__"):
            data = [data]
        if len(data) == 1 and self._subplots:
            data = [data[0]] * len(self._subplots)
        results = []
        for i, field in enumerate(data):
            if i + 1 > len(self.subplots):
                subplot = self._chart.add_subplot(data=field)
            else:
                subplot = self.subplots[i]
            result = subplot.contourf(field, *args, **kwargs)
            results.append(result)
        return results

    def contour(self, data, *args, **kwargs):
        if not hasattr(data, "__len__"):
            data = [data]
        if len(data) == 1 and self._subplots:
            data = [data[0]] * len(self._subplots)
        results = []
        for i, field in enumerate(data):
            if i + 1 > len(self.subplots):
                subplot = self._chart.add_subplot(data=field)
            else:
                subplot = self.subplots[i]
            result = subplot.contour(field, *args, **kwargs)
            results.append(result)
        return results
