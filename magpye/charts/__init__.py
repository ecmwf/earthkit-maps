import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np

from magpye import inputs
from magpye.domains import auto, parse_crs
from magpye.schema import schema

from . import _fonts, layers, styles, titles  # noqa: F401


def await_crs(method):
    def wrapper(self, *args, **kwargs):
        if self._crs is None:
            self._queue.append((method, args, kwargs))
        else:
            return method(self, *args, **kwargs)

    return wrapper


class Chart:
    """
    A geospatial chart containing a single axis.

    Parameters
    ----------
    domain : str or list (optional)
        Must be either:
            - A string naming the domain to use for the chart (e.g. a country,
              continent or state/province).
            - A list containing the bounding box of the domain, in the order
              `[min_x, max_x, min_y, max_y]`. The bounding box is assumed to be
              defined in terms of latitude and longitude values, unless the
              `domain_crs` argument is also passed, in which case the bounding
              box must be defined using `domain_crs` coordinates.
        If no domain is passed, the chart will attempt to use the best domain
        to fit the first field of data plotted on the chart.
    crs : cartopy.crs.CRS (optional)
        The coordinate reference system to use for this chart. If `None`
        (default), will attempt to find the best CRS to suit the bounding box
        of the chart.
    domain_crs : cartopy.crs.CRS (optional)
        Use with `domain` to specify the coordinate system on which the domain
        bounding box is defined.
    figsize : list (optional)
        The width and height (in inches) of the chart. Note that the width of
        the chart may be adjusted slightly if the aspect ratio of your chart
        does not match the figsize.
    """

    def __init__(self, domain=None, crs=None, domain_crs=None, figsize=(10, 10)):
        self._domain = domain
        self._crs = crs
        if self._crs is not None:
            self._crs = parse_crs(self._crs)
        self._domain_crs = domain_crs
        self._bounds = None
        self._boundless = False

        self._queue = []

        self._fig = None
        self._figsize = figsize

        self._ax = None

        self._cbar_axes = None
        self._cbar_locations = None

        self._layers = []

    @staticmethod
    def close_current_fig():
        plt.clf()
        plt.close()

    @property
    def fig(self):
        if self._fig is None:
            self.close_current_fig()
            self._fig = plt.figure(figsize=self._figsize)
        return self._fig

    @property
    def ax(self):
        if self._ax is None:
            self._ax = self.fig.add_subplot(1, 1, 1, projection=self.crs)
            if self.bounds is not None:
                self._ax.set_extent(self.bounds, crs=self.crs)
        return self._ax

    @property
    def size(self):
        bbox = self.ax.get_position()
        return bbox.width, bbox.height

    def is_portrait(self):
        value = self.size[0] < self.size[1]
        return value

    @property
    def bounds(self):
        if self._bounds is None and not self._boundless:
            self._setup_domain()
        return self._bounds

    @property
    def lat_lon_bounds(self):
        return auto.get_crs_extents(self.bounds, ccrs.PlateCarree(), self.crs)

    @property
    def crs(self):
        if self._crs is None:
            self._setup_domain()
        return self._crs

    def _setup_domain(self):
        if self._bounds is None:
            if isinstance(self._domain, (list, tuple)):
                assert len(self._domain) == 4, (
                    f"domains must contain 4 elements ([min_x, max_x, min_y, "
                    f"max_y]); got {len(self._domain)}"
                )
                if self._crs is None:
                    self._crs = auto.get_optimal_crs(self._domain)
                self._bounds = auto.get_crs_extents(
                    self._domain, self._crs, self._domain_crs or schema.reference_crs
                )
            elif isinstance(self._domain, str):
                self._bounds, self._crs = auto.get_bounds_and_crs(
                    self._domain, self._crs
                )
            elif self._domain is None:
                self._crs = self._crs or schema.reference_crs
                self._boundless = True
            else:
                raise ValueError(
                    f"'domain' must be str or list; got {type(self._domain)}"
                )

    @styles.dynamic(normalize=True)
    @layers.append
    @inputs.extract()
    def mesh(self, data, *args, x=None, y=None, **kwargs):
        kwargs.pop("levels", None)
        return self.ax.pcolormesh(x, y, data, *args, **kwargs)

    @styles.dynamic(normalize=True)
    @layers.append
    @inputs.extract()
    def filled_contours(
        self, data, *args, x=None, y=None, transform_first=True, **kwargs
    ):
        x, y = np.meshgrid(x, y)
        return self.ax.contourf(
            x, y, data, *args, transform_first=transform_first, **kwargs
        )

    @layers.append
    @inputs.extract()
    @schema.contour.apply()
    def contour(
        self,
        data,
        *args,
        x=None,
        y=None,
        labels=False,
        label_fontsize=7,
        label_colors=None,
        label_frequency=1,
        label_background=None,
        **kwargs,
    ):
        if "cmap" in kwargs and "colors" in kwargs:
            kwargs.pop("colors")
        contours = self.ax.contour(x, y, data, *args, **kwargs)
        if labels:
            clabels = self.ax.clabel(
                contours,
                contours.levels[0::label_frequency],
                inline=True,
                fontsize=label_fontsize,
                colors=label_colors,
                inline_spacing=2,
            )
            if label_background is not None:
                for label in clabels:
                    label.set_backgroundcolor(label_background)
        return contours

    @schema.apply("font")
    @schema.legend.apply()
    def legend(self, *args, **kwargs):
        layer = self._layers[-1]
        if layer.legend is not False:
            return layer.legend(*args, chart=self, **kwargs)

    def _resize_colorbars(self):
        p = self.ax.get_position()

        offset = {"right": 0, "left": 0, "bottom": 0, "top": 0}

        for layer in self._layers:
            if layer._legend_location is None:
                continue
            position = {
                "right": [
                    p.x0 + p.width + 0.01 + offset["right"],
                    p.y0,
                    0.03,
                    p.height,
                ],
                "left": [p.x0 - 0.04 - offset["left"], p.y0, 0.03, p.height],
                "bottom": [p.x0, p.y0 - 0.04 - offset["bottom"], p.width, 0.03],
                "top": [p.x0, p.y0 + p.height + 0.04 + offset["top"], p.width, 0.03],
            }[layer._legend_location]
            offset[layer._legend_location] += 0.1
            layer._legend_ax.set_position(position)

    @await_crs
    @schema.coastlines.apply()
    def coastlines(self, **kwargs):
        """Add coastal outlines from the Natural Earth “coastline” shapefile collection."""
        return self.ax.coastlines(**kwargs)

    @await_crs
    @schema.borders.apply()
    def borders(self, **kwargs):
        """Add political boundaries from the Natural Earth administrative shapefile collection."""
        return self.ax.add_feature(cfeature.BORDERS, **kwargs)

    @await_crs
    @schema.roads.apply()
    def roads(self, resolution="50m", **kwargs):
        """Add roads from the Natural Earth cultural shapefile collection."""
        feature = cfeature.NaturalEarthFeature("cultural", "roads", "10m")

        return self.ax.add_feature(feature, **kwargs)

    @await_crs
    @schema.gridlines.apply()
    def gridlines(self, **kwargs):
        """Add latitude and longitude gridlines."""
        return self.ax.gridlines(**kwargs)

    @await_crs
    def land(self, **kwargs):
        """Add land polygons from the Natural Earth "land" shapefile collection."""
        return self.ax.add_feature(cfeature.LAND, **kwargs)

    @schema.apply("font")
    @schema.title.apply()
    def title(self, *args, **kwargs):
        if args:
            label = args[0]
            args = args[1:]
        else:
            label = kwargs.pop("labels", None)
        label = titles.format_string(self, label)

        plt.sca(self.ax)
        plt.title(label, *args, **kwargs)

    def _release_queue(self):
        while len(self._queue):
            method, args, kwargs = self._queue.pop(0)
            method(self, *args, **kwargs)

    def show(self, *args, **kwargs):
        """Display the chart."""
        self._release_queue()
        plt.show(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Save the chart."""
        self._release_queue()
        try:
            with open('/app/argskwarg.text', 'w') as f:
                f.write(f'ARGS: {args}\n\n')
                f.write(f'KWARGS: {kwargs}\n\n')
        except:
            pass
        plt.savefig(*args, **kwargs)
