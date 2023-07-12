import glob
import itertools
import os

import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

from earthkit.maps import domains, layers, layout, metadata
from earthkit.maps.definitions import FONTS_DIR
from earthkit.maps.schema import schema


def register_fonts():
    fontpaths = glob.glob(os.path.join(FONTS_DIR, "*"))
    for fontpath in fontpaths:
        font_files = glob.glob(os.path.join(fontpath, "*.ttf"))
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)


register_fonts()
rcParams["font.family"] = schema.font
rcParams["axes.linewidth"] = 0.5


class Chart:
    @classmethod
    def from_fig(cls, fig, **kwargs):
        chart = cls(**kwargs)
        chart._fig = fig
        return chart

    @classmethod
    def from_gridspec(cls, gridspec, **kwargs):
        chart = cls(**kwargs)
        chart._gridspec = gridspec
        return chart

    def __init__(
        self,
        domain=None,
        crs=None,
        rows=None,
        cols=None,
    ):
        self.domain = domains.parse_domain(domain, crs)

        self._fig = None
        self._gridspec = None

        self._axes = None

        self._rows = rows
        self._cols = cols

        self.subplots = layers.Subplots(self)
        self._iter_subplots = None

    @property
    def fig(self):
        if self._fig is None:
            self._fig = plt.figure(figsize=schema.figsize, dpi=schema.dpi)
        return self._fig

    @property
    def rows(self):
        if self._rows is None:
            self._rows = 1
        return self._rows

    @property
    def cols(self):
        if self._cols is None:
            self._cols = 1
        return self._cols

    @property
    def gridspec(self):
        if self._gridspec is None:
            self._gridspec = self.fig.add_gridspec(self.rows, self.cols)
        return self._gridspec

    @property
    def iter_subplots(self):
        if self._iter_subplots is None:
            self._iter_subplots = (
                (i, j)
                for i, j in itertools.product(
                    range(self.gridspec.nrows),
                    range(self.gridspec.ncols),
                )
            )
        return self._iter_subplots

    def expand_subplots(method):
        def wrapper(self, data, *args, **kwargs):
            if self._rows is None:
                if hasattr(data, "__len__"):
                    self._rows, self._cols = layout.auto_rows_cols(len(data))
                else:
                    self._rows, self._cols = 1, 1
            return method(self, data, *args, **kwargs)

        return wrapper

    def add_subplot(self, *args, domain=None, crs=None, data=None, **kwargs):
        i, j = next(self.iter_subplots)

        if not args:
            args = (self.gridspec[i, j],)

        if data is None:
            subplot = layers.Subplot(self, *args, domain=domain, crs=crs, **kwargs)
        else:
            subplot = layers.Subplot.from_data(
                self,
                data,
                *args,
                domain=self.domain.domain_name,
                crs=self.domain.crs,
                **kwargs,
            )

        self.subplots.add_subplot(subplot)
        return subplot

    @property
    def axes(self):
        if not self._axes:
            self.add_subplot()
        return self._axes

    def _global(method):
        def iterate_method(self, *args, **kwargs):
            return getattr(self.subplots, method.__name__)(*args, **kwargs)

        return iterate_method

    @schema.gridlines.apply()
    @_global
    def gridlines(self, *args, **kwargs):
        pass

    @schema.coastlines.apply()
    @_global
    def coastlines(self, *args, **kwargs):
        pass

    @schema.borders.apply()
    @_global
    def borders(self, *args, **kwargs):
        pass

    @schema.land.apply()
    @_global
    def land(self, *args, **kwargs):
        pass

    @schema.ocean.apply()
    @_global
    def ocean(self, *args, **kwargs):
        pass

    @_global
    def stock_img(self, *args, **kwargs):
        pass

    @_global
    def pcolormesh(self, *args, **kwargs):
        pass

    @expand_subplots
    @_global
    def contourf(self, *args, **kwargs):
        pass

    shaded_contour = contourf

    @expand_subplots
    @schema.contour.apply()
    @_global
    def contour(self, *args, **kwargs):
        pass

    def legend(self, *args, **kwargs):
        return self.subplots.legend(*args, **kwargs)

    def subplot_titles(self, *args, **kwargs):
        return [subplot.title(*args, **kwargs) for subplot in self.subplots]

    @schema.title.apply()
    def title(self, label=None, **kwargs):
        label = metadata.labels.title_from_subplot(self.subplots, label)
        if "y" not in kwargs:
            y1 = max(subplot.ax.get_position().y1 for subplot in self.subplots)
            kwargs["y"] = y1 + (0.05 if self.subplots[0]._title is not None else 0.01)
        if not any(kwarg in kwargs for kwarg in ("verticalalignment", "va")):
            kwargs["verticalalignment"] = "bottom"

        return self.fig.suptitle(label, **kwargs)

    def show(self, *args, **kwargs):
        """Display the chart."""
        [subplot._release_queue() for subplot in self.subplots]
        self.subplots._resize_legends()
        plt.show(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Save the chart."""
        [subplot._release_queue() for subplot in self.subplots]
        self.subplots._resize_legends()
        plt.savefig(*args, **kwargs)
