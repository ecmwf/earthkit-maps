
import glob
import os
import itertools

from matplotlib import font_manager, rcParams
import matplotlib.pyplot as plt
import cartopy.feature as cfeature

from earthkit.maps import domains, sources
from earthkit.maps._definitions import FONTS_DIR
from earthkit.maps.charts import titles, layers, styles
from earthkit.maps.schema import schema


def register_fonts():
    fontpaths = glob.glob(os.path.join(FONTS_DIR, "*"))
    for fontpath in fontpaths:
        font_files = glob.glob(os.path.join(fontpath, "*.ttf"))
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)


register_fonts()
rcParams["font.family"] = schema.font


def await_crs(method):
    def wrapper(self, *args, **kwargs):
        if self.domain is None:
            self._queue.append((method, args, kwargs))
        else:
            return method(self, *args, **kwargs)

    return wrapper


class Chart:
    
    def __init__(
            self, figure=None, domain=None, crs=None, figsize=(10, 7.5),
            **kwargs,            
        ):
        self.domain = domains.parse_domain(domain, crs)
        
        if figure is None:
            self.fig = plt.figure(figsize=figsize)
        else:
            self.fig = figure

        if kwargs:
            self._gridspec = self.fig.add_gridspec(**kwargs)
            self._rows = self._gridspec.nrows
            self._cols = self._gridspec.ncols
        else:
            self._gridspec = None
            self._rows = None
            self._cols = None
        self._iter_subplots = None

        self.subplots = layers.Subplots(self)
        self._ax_idx = 0

        self._queue = []
        self._cbars = []
        
        self._gridlines = None
    
    @property
    def iter_subplots(self):
        if self._iter_subplots is None:
            self._iter_subplots = (
                (i, j) for i, j in itertools.product(
                    range(self.gridspec.nrows),
                    range(self.gridspec.ncols),
                )
            )
        return self._iter_subplots
    
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
            self._gridspec = self.fig.add_gridspec(
                nrows=self.rows, ncols=self.cols,
            )
        return self._gridspec
    
    def add_subplot(self, *args, data=None, domain=None, crs=None, **kwargs):        
        # Always increment the unplotted subplots
        i, j = next(self.iter_subplots)
        
        if not args:
            args = (self.gridspec[i, j],)
        
        if data is not None:
            subplot = layers.Subplot.from_data(self, data, *args, **kwargs)
        else:
            subplot = layers.Subplot(self, *args, domain=domain, crs=crs, **kwargs)

        self.subplots.add_subplot(subplot)
        return subplot
    
    def expand_subplots(method):
        def wrapper(self, data, *args, **kwargs):
            if self._rows is None:
                if hasattr(data, "__len__"):
                    self._rows, self._cols = auto_rows_cols(len(data))
                else:
                    self._rows, self._cols = 1, 1
            return method(self, data, *args, **kwargs)
        return wrapper
    
    @property
    def axes(self):
        if not self._axes:
            self.add_subplot()
        return self._axes
    
    @property
    def ax(self):
        return self._axes[self._ax_idx]

    @await_crs
    @schema.coastlines.apply()
    def coastlines(self, **kwargs):
        """Add coastal outlines from the Natural Earth “coastline” shapefile collection."""
        return self.subplots.coastlines(**kwargs)

    @await_crs
    @schema.borders.apply()
    def borders(self, **kwargs):
        """Add political boundaries from the Natural Earth administrative shapefile collection."""
        return self.subplots.add_feature(cfeature.BORDERS, **kwargs)

    @await_crs
    @schema.land.apply()
    def land(self, **kwargs):
        """Add political boundaries from the Natural Earth administrative shapefile collection."""
        return self.subplots.add_feature(cfeature.LAND, **kwargs)

    @await_crs
    @schema.gridlines.apply()
    def gridlines(self, **kwargs):
        """Add latitude and longitude gridlines."""
        self._gridlines = self.subplots.gridlines(**kwargs)
        return self._gridlines

    @expand_subplots
    def pcolormesh(self, data, *args, **kwargs):
        self.subplots.pcolormesh(data, *args, **kwargs)
    
    @expand_subplots
    def contourf(self, data, *args, **kwargs):
        return self.subplots.contourf(data, *args, **kwargs)

    shaded_contour = contourf

    @expand_subplots
    def contour(self, data, *args, **kwargs):
        return self.subplots.contour(data, *args, **kwargs)

    def subplot_titles(self, *args, **kwargs):
        return self.subplots.titles(*args, **kwargs)

    @schema.title.apply()
    def title(self, *args, **kwargs):
        return self.subplots.title(*args, **kwargs)

    def legend(self, *args, **kwargs):
        return self.subplots.legend(*args, **kwargs)

    def _release_queue(self):
        while len(self._queue):
            method, args, kwargs = self._queue.pop(0)
            method(self, *args, **kwargs)

    def show(self, *args, **kwargs):
        """Display the chart."""
        self._release_queue()
        self._resize_colorbars()
        plt.show(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Save the chart."""
        self._release_queue()
        self._resize_colorbars()
        plt.savefig(*args, **kwargs)


    def _resize_colorbars(self):
        positions = [subplot.ax.get_position() for subplot in self.subplots]
        x0 = min(pos.x0 for pos in positions)
        x1 = min(pos.x1 for pos in positions)
        y0 = min(pos.y0 for pos in positions)
        y1 = min(pos.y1 for pos in positions)
        width = x1 - x0
        height = y1 - y0
        
        offset = {"right": 0, "left": 0, "bottom": 0, "top": 0}

        if self._gridlines is not None:
            pad = {"right": 0.045, "left": 0.045, "bottom": 0.02, "top": 0.02}
            for side in offset:
                if getattr(self._gridlines[0], f"{side}_labels"):
                    offset[side] += pad[side]

        for cbar in self._cbars:
            if not getattr(cbar, "auto", False):
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
            }[cbar.location]
            offset[cbar.location] += 0.1
            cbar.ax.set_position(position)


def auto_rows_cols(num_subplots, max_cols=8):
    presets = {
        1: (1, 1),
        2: (1, 2),
        3: (1, 3),
        4: (1, 4),
        5: (2, 3),
        6: (2, 3),
        7: (2, 4),
        8: (2, 4),
        9: (2, 5),
        10: (2, 5),
        11: (3, 4),
        12: (3, 4),
        13: (3, 5),
        14: (3, 5),
        15: (3, 5),
        16: (3, 6),
        17: (3, 6),
        18: (3, 6),
        19: (4, 5),
        20: (4, 5),
    }
    
    if num_subplots in presets:
        rows, cols = presets[num_subplots]
    else:
        cols = max_cols
        rows = num_subplots//max_cols + 1
    
    return rows, cols