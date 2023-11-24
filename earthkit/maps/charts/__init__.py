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

import earthkit.data
import matplotlib.pyplot as plt
import numpy as np

from earthkit.maps import domains, utils
from earthkit.maps.charts import layouts
from earthkit.maps.charts.layers import LayerGroup
from earthkit.maps.charts.subplots import Subplot
from earthkit.maps.metadata.formatters import ChartFormatter
from earthkit.maps.schemas import schema


class Chart:

    MAX_COLS = 8

    @classmethod
    def from_gridspec(cls, gridspec, *args, **kwargs):
        """
        Instantiate an earthkit Superplot from a matplotlib gridspec.

        Parameters
        ----------
        gridspec : matplotlib.gridspec.GridSpec
            A matplotlib grid layout which determines subplot layout.
        *args, **kwargs

        """
        obj = cls(*args, **kwargs)
        obj._gridspec = gridspec
        return obj

    def __init__(self, domain=None, crs=None, rows=None, columns=None):

        self._domain = domain
        self._crs = crs

        self.domain = domains.parse(domain, crs)

        self._fig = None
        self._gridspec = None

        self._rows = rows
        self._columns = columns

        self.subplots = []
        self._subplots_generator = None

        self._queue = []

    def __len__(self):
        return len(self.subplots)

    def __getitem__(self, i):
        while i + 1 > len(self.subplots):
            self.add_subplot()
        return self.subplots[i]

    @property
    def fig(self):
        if self._fig is None:
            self._fig = plt.figure(
                figsize=schema.figsize, constrained_layout=True, dpi=schema.dpi
            )
        return self._fig

    @property
    def gridspec(self):
        if self._gridspec is None:
            self._gridspec = self.fig.add_gridspec(*self.shape)
        return self._gridspec

    @property
    def rows(self):
        if self._rows is None:
            if len(self) == 0:
                raise ValueError("cannot get rows from empty figure")
            self._rows = layouts.rows_cols(
                len(self), cols=self._columns, max_cols=self.MAX_COLS
            )[0]
        return self._rows

    @property
    def cols(self):
        if self._columns is None:
            if len(self) == 0:
                raise ValueError("cannot get cols from empty figure")
            self._columns = layouts.rows_cols(
                len(self), rows=self._rows, max_cols=self.MAX_COLS
            )[1]
        return self._columns

    @property
    def shape(self):
        return self.rows, self.cols

    @property
    def subplots_generator(self):
        if self._subplots_generator is None:
            self._subplots_generator = (
                (row, col)
                for row, col in itertools.product(
                    range(self.gridspec.nrows),
                    range(self.gridspec.ncols),
                )
            )
        return self._subplots_generator

    def add_subplot(self, *args, data=None, domain=None, crs=None, **kwargs):
        row, col = next(self.subplots_generator)

        if domain is None and crs is None:
            domain = self._domain
            crs = self._crs

        if not args:
            args = (self.gridspec[row, col],)

        if data is not None:
            subplot = Subplot.from_data(
                self, data, *args, domain=domain, crs=crs, **kwargs
            )
        else:
            subplot = Subplot(self, *args, domain=domain, crs=crs, **kwargs)

        self.subplots.append(subplot)
        return subplot

    @property
    def distinct_legend_layers(self):
        """Group layers by style."""
        subplot_layers = [subplot.distinct_legend_layers for subplot in self.subplots]
        subplot_layers = [item for sublist in subplot_layers for item in sublist]

        groups = []
        for layer in subplot_layers:
            for i in range(len(groups)):
                if groups[i][0].style == layer.style:
                    groups[i].append(layer)
                    break
            else:
                groups.append([layer])

        groups = [LayerGroup(layers) for layers in list(groups)]

        return groups

    def defer(method):
        """Defer a method's execution until this superplot has subplots."""

        def wrapper(self, *args, **kwargs):
            if not self.subplots:
                self._queue.append((method, args, kwargs))
            else:
                return method(self, *args, **kwargs)

        return wrapper

    def expand_rows_cols(method):
        def wrapper(self, data, *args, **kwargs):
            if not isinstance(data, (earthkit.data.core.Base, list, np.ndarray)):
                data = earthkit.data.from_object(data)
            if not isinstance(data, earthkit.data.core.Base) or not hasattr(
                data, "__len__"
            ):
                data = [data]

            if not self.subplots:
                num_subplots = len(data)
                self._rows, self._columns = layouts.rows_cols(
                    num_subplots,
                    rows=self._rows,
                    cols=self._columns,
                    max_cols=self.MAX_COLS,
                )

            layers = []
            for i, field in enumerate(data):
                if i + 1 > len(self.subplots):
                    subplot = self.add_subplot(data=field)
                else:
                    subplot = self.subplots[i]
                layer = getattr(subplot, method.__name__)(field, *args, **kwargs)
                layers.append(layer)

            return LayerGroup(layers)

        return wrapper

    def plot(self, data, *args, **kwargs):
        if data.__class__.__name__ in ("DataFrame", "Series"):
            raise NotImplementedError(
                "Plotting pandas DataFrames and Series is an upcoming feature"
            )
        else:
            return self._plot_gridded_scalar(data, *args, **kwargs)

    @expand_rows_cols
    def _plot_gridded_scalar(self, *args, **kwargs):
        """
        Plot some data.

        Parameters
        ----------
        data : earthkit.data.core.Base or numpy.ndarray or xarray.Dataset
            The data to plot on the chart.
        x : numpy.ndarray, optional
            The x values of the geos
        y : numpy.ndarray, optional
            The y values of the geos
        transform : cartopy.crs.CCRS, optional
        style : earthkit.maps.styles.Style, optional

        **kwargs : dict, optional
            Extra arguments to pass to the underlying matplotlib plotting
            method.
        """
        pass

    @expand_rows_cols
    def contourf(self, *args, **kwargs):
        pass

    shaded_contour = contourf

    @expand_rows_cols
    def contour(self, *args, **kwargs):
        pass

    @expand_rows_cols
    def pcolormesh(self, *args, **kwargs):
        pass

    @expand_rows_cols
    def scatter(self, *args, **kwargs):
        pass

    def polygons(self, *args, **kwargs):
        if not self.subplots:
            self._rows, self._columns = (1, 1)
            self.add_subplot()
        [subplot.polygons(*args, **kwargs) for subplot in self.subplots]

    @defer
    def coastlines(self, *args, **kwargs):
        return [subplot.coastlines(*args, **kwargs) for subplot in self.subplots]

    @defer
    def borders(self, *args, **kwargs):
        return [subplot.borders(*args, **kwargs) for subplot in self.subplots]

    @defer
    def land(self, *args, **kwargs):
        return [subplot.land(*args, **kwargs) for subplot in self.subplots]

    @defer
    def ocean(self, *args, **kwargs):
        return [subplot.ocean(*args, **kwargs) for subplot in self.subplots]

    @defer
    def stock_img(self, *args, **kwargs):
        return [subplot.stock_img(*args, **kwargs) for subplot in self.subplots]

    @defer
    def gridlines(self, *args, **kwargs):
        return [subplot.gridlines(*args, **kwargs) for subplot in self.subplots]

    def format_string(self, string, unique=True, grouped=True):
        if not grouped:
            results = [
                subplot.format_string(string, unique, grouped)
                for subplot in self.subplots
            ]
            result = utils.list_to_human(results)
        else:
            result = ChartFormatter(self.subplots, unique=unique).format(string)
        return result

    def _release_queue(self):
        while len(self._queue):
            method, args, kwargs = self._queue.pop(0)
            method(self, *args, **kwargs)

    @schema.legend.apply()
    def legend(self, *args, location=None, **kwargs):
        legends = []

        anchor = None
        non_cbar_layers = []
        for i, layer in enumerate(self.distinct_legend_layers):
            if isinstance(location, (list, tuple)):
                loc = location[i]
            else:
                loc = location
            if layer.style is not None:
                legend = layer.style.legend(
                    layer,
                    *args,
                    location=loc,
                    **kwargs,
                )
            if legend.__class__.__name__ != "Colorbar":
                non_cbar_layers.append(layer)
            else:
                anchor = layer.axes[0].get_anchor()
            legends.append(legend)

        if anchor is not None:
            for layer in non_cbar_layers:
                for ax in layer.axes:
                    ax.set_anchor(anchor)

        return legends

    @defer
    def add_geometries(self, *args, **kwargs):
        """
        Plot geometries on all subplots.

        Parameters
        ----------
        shapes : geopandas.GeoDataFrame or earthkit.data

        shapes, *args, crs=None, labels=False, label_kwargs=None, **kwargs
        """
        return [subplot.add_geometries(*args, **kwargs) for subplot in self.subplots]

    @property
    def _default_title_template(self):
        return self.subplots[0]._default_title_template

    @defer
    @schema.title.apply()
    def title(self, label=None, unique=True, grouped=True, y=None, **kwargs):
        """
        Add a top-level title to the chart.

        Parameters
        ----------
        label : str, optional
            The text to use in the title. This text can include format keys
            surrounded by `{}` curly brackets, which will extract metadata from
            your plotted data layers.
        unique : bool, optional
            If True, format keys which are uniform across subplots/layers will
            produce a single result. For example, if all data layers have the
            same `variable_name`, only one variable name will appear in the
            title.
            If False, each format key will evaluate to a list of values found
            across subplots/layers.
        grouped : bool, optional
            If True, a single title will be generated to represent all data
            layers, with each format key evaluating to a list where layers
            differ - e.g. `"{variable} at {time}"` might be evaluated to
            `"temperature and wind at 2023-01-01 00:00".
            If False, the title will be duplicated by the number of subplots/
            layers - e.g. `"{variable} at {time}"` might be evaluated to
            `"temperature at 2023-01-01 00:00 and wind at 2023-01-01 00:00".
        kwargs : dict, optional
            Keyword argument to matplotlib.pyplot.suptitle (see
            https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html#matplotlib-pyplot-suptitle
            ).
        """
        if label is None:
            label = self._default_title_template
        label = self.format_string(label, unique, grouped)

        # if y is None:
        #     y = 0
        #     for subplot in self:
        #         y = max(y, subplot.ax.get_position().y1)
        #         if subplot.ax.title.get_text():
        #             y += 0.05
        #     kwargs["va"] = kwargs.get("va", kwargs.get("verticalalignment", "bottom"))

        self.fig.canvas.draw()
        return self.fig.suptitle(label, y=y, **kwargs)

    @defer
    def subplot_titles(self, *args, **kwargs):
        if args and isinstance(args[0], (list, tuple)):
            items = args[0]
            args = args[1:]
            return [
                subplot.title(item, *args, **kwargs)
                for item, subplot in zip(items, self.subplots)
            ]
        return [subplot.title(*args, **kwargs) for subplot in self.subplots]

    def show(self, *args, **kwargs):
        """Display the chart."""
        if len(self) == 0:
            self._rows, self._columns = (1, 1)
            self.add_subplot()
        self._release_queue()
        plt.show(*args, **kwargs)

    def save(self, *args, bbox_inches="tight", **kwargs):
        """Save the chart."""
        if len(self) == 0:
            self._rows, self._columns = (1, 1)
            self.add_subplot()
        self._release_queue()
        return plt.savefig(*args, bbox_inches=bbox_inches, **kwargs)
