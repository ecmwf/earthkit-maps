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

import matplotlib as mpl
import matplotlib.pyplot as plt

from earthkit.maps import metadata, schema, styles
from earthkit.maps.styles import colors, legends, levels

__all__ = [
    "colors",
    "legends",
    "levels",
]


class Style:
    """
    Class describing a mapping style.

    Parameters
    ----------
    colors : str or list or matplotlib.colors.Colormap, optional
        The colors to be used in this `Style`. This can be a
        `named matplotlib colormap <https://matplotlib.org/stable/gallery/color/colormap_reference.html>`__,
        a list of colors (as named CSS4 colors, hexadecimal colors or three
        (four)-element lists of RGB(A) values), or a pre-defined matplotlib
        colormap object. If not provided, the default colormap of the active
        `schema` will be used.
    levels : list or earthkit.maps.styles.levels.Levels, optional
        The levels to use in this `Style`. This can be a list of specific
        levels, or an earthkit `Levels` object. If not provided, some suitable
        levels will be generated automatically (experimental!).
    normalize : bool, optional
        If `True` (default), then the colors will be normalized over the level
        range.
    units : str, optional
        The units in which the levels are defined. If this `Style` is used with
        data not using the given units, then a conversion will be attempted;
        any data incompatible with these units will not be able to use this
        `Style`. If `units` are not provided, then data plotted using this
        `Style` will remain in their original units.
        Note that passing `units` requires `cf_units` to be installed.
    units_label : str, optional
        The label to use in titles and legends to represent the units of the
        data.
    legend_style : str, optional
        The style of legend to use by default with this style. Must be one of
        `colorbar` (default), `disjoint` or `histogram`.
    bin_labels : list, optional
        A list of categorical labels for each bin in the legend.
    """

    def __init__(
        self,
        colors=schema.cmap,
        levels=None,
        normalize=True,
        units=None,
        units_label=None,
        legend_style="colorbar",
        legend_kwargs=None,
        bin_labels=None,
        ticks=None,
        **kwargs,
    ):
        self._colors = colors
        self._levels = (
            levels
            if isinstance(levels, styles.levels.Levels)
            else styles.levels.Levels(levels)
        )
        self.normalize = normalize

        if units is not None and metadata.units._NO_CF_UNITS:
            warnings.warn(
                "You must have cf-units installed to use unit conversion "
                "features; since no cf-units installation was found, no units "
                "will be applied to this style"
            )
            units = None
        self._units = units
        self._units_label = units_label

        self._legend_style = legend_style
        self._bin_labels = bin_labels
        self._legend_kwargs = legend_kwargs or dict()
        if ticks is not None:
            self._legend_kwargs["ticks"] = ticks

        self._kwargs = kwargs

    def levels(self, data):
        """
        Generate levels specific to some data.

        Parameters
        ----------
        data : numpy.ndarray or xarray.DataArray or earthkit.data.core.Base
            The data for which to generate a list of levels.

        Returns
        -------
        list
        """
        return self._levels.apply(data)

    @property
    def units(self):
        """Formatted units for use in figure text."""
        if self._units_label is not None:
            return self._units_label
        elif self._units is not None:
            return metadata.units.format_units(self._units)

    def convert_units(self, values, source_units, short_name=""):
        """
        Convert some values from their source units to this `Style`'s units.

        Parameters
        ----------
        values : numpy.ndarray
            The values to convert from their source units to this `Style`'s
            units.
        source_units : str or cf_units.Unit
            The source units of the given values.
        short_name : str, optional
            The short name of the variable, which is used to make extra
            assumptions about the data's unit covnersion (for example,
            temperature anomalies need special consideration when converting
            between Celsius and Kelvin).
        """
        if self._units is None or source_units is None:
            return values

        # For temperature anomalies we do not want to convert values, just
        # change the units string
        if "anomaly" in short_name.lower() and metadata.units.anomaly_equivalence(
            source_units
        ):
            return values

        return metadata.units.convert(values, source_units, self._units)

    def to_matplotlib_kwargs(self, data):
        """
        Generate matplotlib arguments required for plotting data in this `Style`.

        Parameters
        ----------
        data : numpy.ndarray
            The data to be plotted using this `Style`.
        """
        levels = self.levels(data)
        cmap, norm = styles.colors.cmap_and_norm(
            self._colors,
            levels,
            self.normalize,
        )

        return {
            **{"cmap": cmap, "norm": norm, "levels": levels},
            **self._kwargs,
        }

    def to_contourf_kwargs(self, data):
        """
        Generate `contourf` arguments required for plotting data in this `Style`.

        Parameters
        ----------
        data : numpy.ndarray
            The data to be plotted using this `Style`.
        """
        kwargs = self.to_matplotlib_kwargs(data)
        kwargs.pop("linewidths", None)
        return kwargs

    def to_contour_kwargs(self, data):
        """
        Generate `contour` arguments required for plotting data in this `Style`.

        Parameters
        ----------
        data : numpy.ndarray
            The data to be plotted using this `Style`.
        """
        return self.to_matplotlib_kwargs(data)

    def to_pcolormesh_kwargs(self, data):
        """
        Generate `pcolormesh` arguments required for plotting data in this `Style`.

        Parameters
        ----------
        data : numpy.ndarray
            The data to be plotted using this `Style`.
        """
        kwargs = self.to_matplotlib_kwargs(data)
        kwargs.pop("levels", None)
        kwargs.pop("transform_first", None)
        kwargs.pop("extend", None)
        return kwargs

    def to_scatter_kwargs(self, data):
        """
        Generate `scatter` arguments required for plotting data in this `Style`.

        Parameters
        ----------
        data : numpy.ndarray
            The data to be plotted using this `Style`.
        """
        kwargs = self.to_matplotlib_kwargs(data)
        kwargs.pop("levels", None)
        return kwargs

    def plot(self, *args, **kwargs):
        """Plot the data using the `Style`'s defaults."""
        raise NotImplementedError("Generic styles cannot be used with 'plot'")

    def contourf(self, ax, x, y, values, *args, **kwargs):
        """
        Plot shaded contours using this `Style`.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes on which to plot the data.
        x : numpy.ndarray
            The x coordinates of the data to be plotted.
        y : numpy.ndarray
            The y coordinates of the data to be plotted.
        values : numpy.ndarray
            The values of the data to be plotted.
        **kwargs
            Any additional arguments accepted by `matplotlib.axes.Axes.contourf`.
        """
        kwargs = {**self.to_contourf_kwargs(values), **kwargs}
        return ax.contourf(x, y, values, *args, **kwargs)

    def tricontourf(self, ax, x, y, values, *args, **kwargs):
        """
        Plot triangulated shaded contours using this `Style`.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes on which to plot the data.
        x : numpy.ndarray
            The x coordinates of the data to be plotted.
        y : numpy.ndarray
            The y coordinates of the data to be plotted.
        values : numpy.ndarray
            The values of the data to be plotted.
        **kwargs
            Any additional arguments accepted by `matplotlib.axes.Axes.tricontourf`.
        """
        kwargs = {**self.to_contourf_kwargs(values), **kwargs}
        return ax.tricontourf(x, y, values, *args, **kwargs)

    def contour(self, ax, x, y, values, *args, **kwargs):
        """
        Plot line contours using this `Style`.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes on which to plot the data.
        x : numpy.ndarray
            The x coordinates of the data to be plotted.
        y : numpy.ndarray
            The y coordinates of the data to be plotted.
        values : numpy.ndarray
            The values of the data to be plotted.
        **kwargs
            Any additional arguments accepted by `matplotlib.axes.Axes.contour`.
        """
        kwargs = {**self.to_contour_kwargs(values), **kwargs}
        return ax.contour(x, y, values, *args, **kwargs)

    def pcolormesh(self, ax, x, y, values, *args, **kwargs):
        """
        Plot a pcolormesh using this `Style`.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes on which to plot the data.
        x : numpy.ndarray
            The x coordinates of the data to be plotted.
        y : numpy.ndarray
            The y coordinates of the data to be plotted.
        values : numpy.ndarray
            The values of the data to be plotted.
        **kwargs
            Any additional arguments accepted by `matplotlib.axes.Axes.pcolormesh`.
        """
        kwargs.pop("transform_first", None)
        kwargs = {**self.to_pcolormesh_kwargs(values), **kwargs}
        return ax.pcolormesh(x, y, values, *args, **kwargs)

    def scatter(self, ax, x, y, values, s=3, *args, **kwargs):
        """
        Plot a scatter plot using this `Style`.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes on which to plot the data.
        x : numpy.ndarray
            The x coordinates of the data to be plotted.
        y : numpy.ndarray
            The y coordinates of the data to be plotted.
        values : numpy.ndarray
            The values of the data to be plotted.
        **kwargs
            Any additional arguments accepted by `matplotlib.axes.Axes.scatter`.
        """
        kwargs.pop("transform_first", None)
        kwargs = {**self.to_scatter_kwargs(values), **kwargs}
        return ax.scatter(x, y, c=values, s=s, *args, **kwargs)

    def legend(self, *args, **kwargs):
        """Create the default legend for this `Style`."""
        if self._legend_style is None:
            return

        try:
            method = getattr(styles.legends, self._legend_style)
        except AttributeError:
            raise AttributeError(f"invalid legend type '{self._legend_style}'")

        return method(*args, **kwargs)

    def save_legend_graphic(self, data, filename="legend.png", **kwargs):
        backend = mpl.get_backend()
        mpl.use("Agg")
        try:
            getattr(self, f"_save_{self._legend_style}_graphic")(data, filename, kwargs)
        finally:
            mpl.use(backend)

    def _save_colorbar_graphic(self, data, filename, kwargs):
        from earthkit.maps import Chart

        chart = Chart()
        chart.contourf(data, style=self)

        legend = chart.legend(**kwargs)

        chart.fig.canvas.draw()
        bbox = legend.ax.get_window_extent().transformed(
            chart.fig.dpi_scale_trans.inverted()
        )

        title_bbox = legend.ax.xaxis.label.get_window_extent().transformed(
            chart.fig.dpi_scale_trans.inverted()
        )

        x, y = chart.fig.get_size_inches()

        xmod, ymod = (
            (0.05, 0.01) if legend.orientation == "horizontal" else (0.01, 0.05)
        )

        bbox.x0 = min(bbox.x0, title_bbox.x0) - x * xmod
        bbox.x1 = max(bbox.x1, title_bbox.x1) + x * xmod
        bbox.y0 = min(bbox.y0, title_bbox.y0) - y * ymod
        bbox.y1 = max(bbox.y1, title_bbox.y1) + y * ymod

        plt.savefig(filename, dpi="figure", bbox_inches=bbox)

    def _save_disjoint_graphic(self, data, filename, kwargs):
        from earthkit.maps import Chart

        chart = Chart()
        chart.contourf(data, style=self)

        legend = chart.legend(**kwargs)

        chart.fig.canvas.draw()
        fig = legend.figure
        fig.canvas.draw()
        bbox = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(filename, dpi="figure", bbox_inches=bbox)

        plt.savefig(filename, dpi="figure", bbox_inches=bbox)


def auto(data, units=None):
    return Style(colors=schema.cmap)
