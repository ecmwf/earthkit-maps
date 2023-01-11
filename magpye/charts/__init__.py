import cartopy.feature as cfeature
import matplotlib.pyplot as plt

from magpye.domains import auto
from magpye.schema import schema


def await_crs(method):
    def wrapper(self, *args, **kwargs):
        if self._crs is None:
            self._queue.append((method, args, kwargs))
        else:
            return method(self, *args, **kwargs)

    return wrapper


class Chart:
    """The base chart from which all other magpye charts inherit."""

    def __init__(self, *, domain=None, crs=None, domain_crs=None, figsize=(10, 10)):
        self._domain = domain
        self._crs = crs
        self._domain_crs = domain_crs
        self._bounds = None

        self._queue = []

        self._fig = None
        self._figsize = figsize

        self._axis = None

        self._cbar_axes = None
        self._cbar_locations = None

        self._layers = dict()

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
    def axis(self):
        if self._axis is None:
            self._axis = self.fig.add_subplot(1, 1, 1, projection=self.crs)
            if self.bounds is not None:
                self._axis.set_extent(self.bounds, crs=self.crs)
        return self._axis

    @property
    def bounds(self):
        if self._bounds is None:
            self._setup_domain()
        return self._bounds

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
            else:
                raise ValueError(
                    f"'domain' must be str or list; got {type(self._domain)}"
                )

    @await_crs
    @schema.coastlines.apply()
    def coastlines(self, **kwargs):
        return self.axis.coastlines(**kwargs)

    @await_crs
    @schema.borders.apply()
    def borders(self, **kwargs):
        return self.axis.add_feature(cfeature.BORDERS, **kwargs)

    @await_crs
    @schema.gridlines.apply()
    def gridlines(self, **kwargs):
        return self.axis.gridlines(**kwargs)

    @await_crs
    def land(self, **kwargs):
        return self.axis.add_feature(cfeature.LAND, **kwargs)

    def show(self):
        while len(self._queue):
            method, args, kwargs = self._queue.pop(0)
            method(self, *args, **kwargs)
        plt.show()
