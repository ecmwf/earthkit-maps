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

import math

import earthkit.data
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from cf_units import Unit
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap
from matplotlib.patches import Rectangle

from earthkit.maps.layers import metadata
from earthkit.maps.schemas import schema

DEFAULT_LEGEND_LABEL = "{variable_name} ({units})"


def auto_range(data, n_levels=8):

    if isinstance(data, earthkit.data.core.Base):
        data = data.to_numpy()
    min_value = np.nanmin(data)
    max_value = np.nanmax(data)

    data_range = max_value - min_value

    initial_bin = data_range / n_levels

    magnitude = 10 ** (math.floor(math.log(initial_bin, 10)))
    bin_width = initial_bin - (initial_bin % -magnitude)

    start = min_value - (min_value % magnitude)

    levels = list(np.arange(start, start + bin_width * n_levels + bin_width, bin_width))

    while levels[-2] > max_value:
        levels = levels[:-1]

    return levels


def step_range(data, step, multiple=None):

    if multiple is None:
        multiple = step

    if isinstance(data, earthkit.data.core.Base):
        data = data.to_numpy()
    min_value = np.nanmin(data)
    max_value = np.nanmax(data)

    min_value = min_value - (min_value % multiple)
    max_value = int(math.ceil(max_value / multiple)) * multiple

    levels = np.arange(min_value, max_value + step, step)
    return levels


def expand_colors(colors, levels):
    if isinstance(colors, (list, tuple)) and len(colors) == 1:
        colors *= len(levels) - 1
    if isinstance(colors, str):
        try:
            cmap = mpl.cm.get_cmap(colors)
        except ValueError:
            colors = [colors] * (len(levels) - 1)
        else:
            colors = [mpl.cm.get_cmap(cmap)(i) for i in np.linspace(0, 1, len(levels))]
    return colors


class Style:
    def __init__(
        self,
        colors="auto",
        levels=None,
        level_step=None,
        level_multiple=None,
        units=None,
        units_override=None,
        normalize=True,
        legend_type="colorbar",
        categories=None,
        conversion=None,
        **kwargs,
    ):
        if colors == "auto":
            self._colors = schema.cmap
        else:
            self._colors = colors

        self._levels = levels
        self._level_step = level_step
        self._level_multiple = level_multiple

        self.legend_type = legend_type

        self._units = units
        self._units_override = units_override
        self.normalize = normalize
        self.kwargs = kwargs

        self.conversion = conversion

        self._categories = categories

    @property
    def units(self):
        if self._units_override is not None:
            return metadata.format_units(self._units_override)
        elif self._units is not None:
            return metadata.format_units(self._units)

    def convert_units(self, values, source_units):
        if self.conversion is not None:
            values = self.conversion(values)

        if self._units is None:
            return values
        return Unit(source_units).convert(values, self._units)

    def levels(self, data):
        if self._levels is None:
            if self._level_step is None:
                return auto_range(data)
            else:
                return step_range(data, self._level_step, self._level_multiple)
        return self._levels

    def get_levels(self, layer):
        return layer.mappable.norm.boundaries

    def to_kwargs(self, data):
        levels = self.levels(data)

        colors = expand_colors(self._colors, levels)

        cmap = LinearSegmentedColormap.from_list(name="", colors=colors, N=len(colors))

        norm = None
        if self.normalize:
            norm = BoundaryNorm(levels, cmap.N)

        return {
            **{"cmap": cmap, "norm": norm, "levels": levels},
            **self.kwargs,
        }

    def to_contourf_kwargs(self, data):
        kwargs = self.to_kwargs(data)
        kwargs.pop("linewidths", None)
        return kwargs

    def to_contour_kwargs(self, data):
        return self.to_kwargs(data)

    def to_pcolormesh_kwargs(self, data):
        kwargs = self.to_kwargs(data)
        kwargs.pop("levels", None)
        kwargs.pop("transform_first", None)
        kwargs.pop("extend", None)
        return kwargs

    def to_scatter_kwargs(self, data):
        kwargs = self.to_kwargs(data)
        kwargs.pop("levels", None)
        return kwargs

    def plot(self, *args, **kwargs):
        raise NotImplementedError("Generic styles cannot be used with 'plot'")

    def contourf(self, ax, x, y, values, *args, **kwargs):
        kwargs = {**self.to_contourf_kwargs(values), **kwargs}
        return ax.contourf(x, y, values, *args, **kwargs)

    def contour(self, ax, x, y, values, *args, **kwargs):
        kwargs = {**self.to_contour_kwargs(values), **kwargs}
        return ax.contour(x, y, values, *args, **kwargs)

    def pcolormesh(self, ax, x, y, values, *args, **kwargs):
        kwargs.pop("transform_first", None)
        kwargs = {**self.to_pcolormesh_kwargs(values), **kwargs}
        return ax.pcolormesh(x, y, values, *args, **kwargs)

    def scatter(self, ax, x, y, values, s=3, *args, **kwargs):
        kwargs.pop("transform_first", None)
        kwargs = {**self.to_scatter_kwargs(values), **kwargs}
        return ax.scatter(x, y, c=values, s=s, *args, **kwargs)

    def colorbar(self, fig, layer, *args, shrink=0.8, aspect=35, **kwargs):
        label = kwargs.pop("label", DEFAULT_LEGEND_LABEL)
        label = layer.format_string(label)

        levels = self.get_levels(layer)
        if len(np.unique(np.ediff1d(levels))) > 1:
            kwargs["ticks"] = kwargs.get("ticks", levels)
        kwargs["format"] = kwargs.get("format", lambda x, _: f"{x:g}")

        colorbar = fig.colorbar(
            layer.mappable,
            *args,
            label=label,
            shrink=shrink,
            aspect=aspect,
            **kwargs,
        )
        colorbar.ax.minorticks_off()

        return colorbar

    def disjoint_legend(
        self, fig, layer, ax, *args, location="bottom", frameon=False, **kwargs
    ):
        kwargs.pop("format")

        label = kwargs.pop("label", DEFAULT_LEGEND_LABEL)
        label = layer.format_string(label)

        source = ax[0] if len(ax) == 1 else fig

        location_kwargs = {
            "bottom": {
                "loc": "upper center",
                "bbox_to_anchor": (0.5, -0.05),
            },
            "top": {
                "loc": "lower center",
                "bbox_to_anchor": (0.5, 1.0),
            },
            "left": {
                "loc": "upper right",
                "bbox_to_anchor": (-0.05, 1.0),
            },
            "right": {
                "loc": "upper left",
                "bbox_to_anchor": (1.05, 1.0),
            },
            "top left": {
                "loc": "lower center",
                "bbox_to_anchor": (0.25, 1),
            },
            "top right": {
                "loc": "lower center",
                "bbox_to_anchor": (0.75, 1),
            },
        }[location]

        artists, labels = layer.mappable.legend_elements()

        labels = kwargs.pop("labels", self._categories) or labels

        legend = source.legend(
            artists,
            labels,
            *args,
            title=label,
            frameon=frameon,
            **{**location_kwargs, **kwargs},
        )

        # Matplotlib removes legends when a new legend is plotted, so we have
        # to manually re-add them...
        if hasattr(fig, "_previous_legend"):
            fig.add_artist(fig._previous_legend)
        fig._previous_legend = legend

        return legend

    disjoint = disjoint_legend

    def histogram_legend(self, fig, layer, *args, aspect=20, **kwargs):
        label = kwargs.pop("label", DEFAULT_LEGEND_LABEL)
        label = layer.format_string(label)

        colorbar = self.colorbar(fig, layer, *args, aspect=aspect, label="", **kwargs)
        colorbar.outline.set_linestyle(":")
        colorbar.outline.set_alpha(0.5)
        cax = colorbar.ax
        cax.clear()

        levels = self.get_levels(layer)

        location = kwargs.get("location")
        orientation = "vertical" if location in ("top", "bottom") else "horizontal"

        if location in ("top", "bottom"):
            orientation = "vertical"
            cax.xaxis.set_label_position("bottom")
            cax.xaxis.set_ticks_position("bottom")
            cax.set_xlabel(label)
        else:
            orientation = "horizontal"
            cax.yaxis.set_label_position("left")
            cax.yaxis.set_ticks_position("left")
            cax.set_ylabel(label)

        n, bins, patches = cax.hist(
            layer.layers[0].data,
            orientation=orientation,
            bins=levels,
        )

        patch_height = -max(n) / 5
        colors = [layer.mappable.cmap(i) for i in np.linspace(0, 1, len(levels))]

        if orientation == "vertical":
            cax.set_xlim([levels[0], levels[-1]])
            cax.set_ylim([patch_height, None])
            for i in range(len(levels) - 1):
                cax.add_patch(
                    Rectangle(
                        (levels[i], patch_height),
                        levels[i + 1] - levels[i],
                        -patch_height,
                        facecolor=colors[i],
                        edgecolor="black",
                        linewidth=0.5,
                    )
                )
        else:
            cax.set_ylim([levels[0], levels[-1]])
            cax.set_xlim([patch_height, None])
            for i in range(len(levels) - 1):
                cax.add_patch(
                    Rectangle(
                        (patch_height, levels[i]),
                        -patch_height,
                        levels[i + 1] - levels[i],
                        facecolor=colors[i],
                        edgecolor="black",
                        linewidth=0.5,
                    )
                )

        for c, p in zip(colors, patches):
            plt.setp(p, "facecolor", c)
            plt.setp(p, "edgecolor", None)

        return patches

    histogram = histogram_legend

    def legend(self, *args, **kwargs):
        if self.legend_type is None:
            return

        try:
            method = getattr(self, self.legend_type)
        except AttributeError:
            raise AttributeError(f"invalid legend type '{self.legend_type}'")

        return method(*args, **kwargs)


class Contour(Style):
    def __init__(
        self,
        *args,
        colors=None,
        line_colors=None,
        labels=False,
        label_kwargs=None,
        interpolate=True,
        **kwargs,
    ):
        super().__init__(*args, colors=colors, **kwargs)
        self._line_colors = line_colors
        self.labels = labels
        self._label_kwargs = label_kwargs or dict()
        self._interpolate = interpolate
        self.kwargs["linewidths"] = kwargs.get("linewidths", 0.5)

    def get_levels(self, layer):
        return layer.mappable.levels

    def plot(self, *args, **kwargs):
        if self._colors is not None:
            if self._interpolate:
                return self.contourf(*args, **kwargs)
            else:
                return self.pcolormesh(*args, **kwargs)
        else:
            return self.contour(*args, **kwargs)

    def to_kwargs(self, data):
        levels = self.levels(data)

        colors = self._colors
        if colors is None:
            colors = self._line_colors or schema.cmap
        colors = expand_colors(colors, levels)

        cmap = LinearSegmentedColormap.from_list(name="", colors=colors, N=len(colors))

        norm = None
        if self.normalize:
            norm = BoundaryNorm(levels, cmap.N)

        return {
            **{"cmap": cmap, "norm": norm, "levels": levels},
            **self.kwargs,
        }

    def to_contour_kwargs(self, data):
        kwargs = super().to_contour_kwargs(data)

        if self._colors and self._line_colors:
            colors = expand_colors(self._line_colors, kwargs["levels"])
            kwargs["cmap"] = LinearSegmentedColormap.from_list(
                name="", colors=colors, N=len(colors)
            )

        return kwargs

    def contourf(self, ax, x, y, values, *args, **kwargs):
        mappable = super().contourf(ax, x, y, values, *args, **kwargs)
        if self._line_colors is not None:
            self.contour(ax, x, y, values, *args, **kwargs)
        return mappable

    def contour(self, *args, **kwargs):
        mappable = super().contour(*args, **kwargs)

        if self.labels:
            self.contour_labels(mappable, **self._label_kwargs)

        return mappable

    def contour_labels(
        self,
        mappable,
        label_fontsize=7,
        label_colors=None,
        label_frequency=1,
        label_background=None,
        label_fmt=None,
    ):
        clabels = mappable.axes.clabel(
            mappable,
            mappable.levels[0::label_frequency],
            inline=True,
            fontsize=label_fontsize,
            colors=label_colors,
            fmt=label_fmt,
            inline_spacing=2,
        )
        if label_background is not None:
            for label in clabels:
                label.set_backgroundcolor(label_background)

        return clabels


class Continuous(Contour):
    def __init__(self, *args, gradients=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.gradients = gradients

    def to_kwargs(self, data):
        levels = self.levels(data)

        colors = self._colors
        if colors is None:
            colors = self._line_colors or schema.cmap
        colors = expand_colors(colors, levels)

        normalised = (levels - np.min(levels)) / (np.max(levels) - np.min(levels))
        color_bins = list(zip(normalised, colors))
        cmap = LinearSegmentedColormap.from_list(name="", colors=color_bins, N=255)

        gradients = self.gradients or [int(255 / len(levels))] * (len(levels) - 1)
        if not isinstance(gradients, (list, tuple)):
            gradients = [gradients] * (len(levels) - 1)

        extrapolated_levels = []
        for i in range(len(levels) - 1):
            bins = list(np.linspace(levels[i], levels[i + 1], gradients[i]))
            extrapolated_levels += bins[(1 if i != 0 else 0) :]
        levels = extrapolated_levels

        norm = None
        if self.normalize:
            norm = BoundaryNorm(levels, cmap.N)

        cmap.set_bad("#D9D9D9", 1.0)

        return {
            **{"cmap": cmap, "norm": norm, "levels": levels},
            **self.kwargs,
        }

    def colorbar(self, *args, ticks=None, **kwargs):
        return super().colorbar(*args, ticks=ticks, **kwargs)


class Hatched(Contour):
    def __init__(self, *args, hatches=".", background_colors=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hatches = hatches
        self._foreground_colors = self._colors
        self._colors = background_colors or [(0, 0, 0, 0)]

    def contourf(self, *args, **kwargs):
        mappable = super().contourf(*args, hatches=self.hatches, **kwargs)

        colors = expand_colors(self._foreground_colors, mappable.levels)

        for i, collection in enumerate(mappable.collections):
            collection.set_edgecolor(colors[i])
            collection.set_linewidth(0)

        return mappable

    def colorbar(self, *args, **kwargs):
        colorbar = super().colorbar(*args, **kwargs)

        levels = colorbar.mappable.levels

        colors = expand_colors(self._foreground_colors, levels)
        for i, artist in enumerate(colorbar.solids_patches):
            artist.set_edgecolor(colors[i])

        return colorbar

    def disjoint(self, fig, layer, ax, *args, **kwargs):
        legend = super().disjoint(fig, layer, ax, *args, **kwargs)

        colors = expand_colors(self._foreground_colors, layer.mappable.levels)

        for color, artist in zip(colors, legend.get_patches()):
            artist.set_edgecolor(color)
            artist.set_linewidth(0.0)

        return legend


class Scatter(Style):
    def plot(self, *args, **kwargs):
        return self.scatter(*args, **kwargs)

    def get_levels(self, layer):
        return self.levels([layer.mappable.norm.vmin, layer.mappable.norm.vmax])


DEFAULT_STYLE = Style(colors=schema.cmap)
