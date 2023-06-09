import matplotlib.pyplot as plt

from earthkit.maps import domains
from earthkit.maps.schema import schema

from . import styles, titles

PRETTY_UNITS = {
    "celsius": "°C",
    "fahrenheit": "°F",
}


def compare_units(unit_1, unit_2):
    from cf_units import Unit

    return Unit(unit_1) == Unit(unit_2)


class DataLayer:
    def __init__(self, data, layer, legend=None, units=None):
        self.data = data
        self.layer = layer
        self._legend = legend
        self._legend_location = None
        self._legend_ax = None
        self._legend_position_default = False
        self._units = units

    @property
    def units(self):
        from cf_units import Unit
        from cf_units.tex import tex

        if self._units is None:
            self._units = self.data.metadata("units")
        for name, unit in PRETTY_UNITS.items():
            if compare_units(self._units, name):
                break
        else:
            unit = Unit(self._units).symbol
        return f"${tex(unit)}$"


class Subplot:

    DATA_LAYER_METHODS = [
        "contour",
        "contourf",
    ]

    LEGENDS = {
        "contour": False,
        "contourf": True,
    }

    @classmethod
    def from_data(cls, chart, data, *args, **kwargs):
        crs = None
        if chart.domain.crs is None:
            crs = data.crs()
        return cls(chart, *args, crs=crs, **kwargs)

    def __init__(self, chart, *args, domain=None, crs=None, **kwargs):
        if domain is None and crs is None:
            self.domain = chart.domain
        else:
            self.domain = domains.parse_domain(domain, crs)
        self.ax = chart.fig.add_subplot(*args, projection=self.domain.crs, **kwargs)
        if self.domain.bounds is not None:
            self.ax.set_extent(self.domain.bounds, crs=self.domain.crs)

        self.layers = []
        self._chart = chart

    def __getattr__(self, attr):
        if attr in self.DATA_LAYER_METHODS:
            legend = self.LEGENDS.get(attr, False)
            return self.add_layer(getattr(self.ax, attr), legend=legend)
        try:
            method = getattr(self.ax, attr)
        except AttributeError:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{attr}'")
        return method

    @property
    def _default_fontsize(self):
        font_sizes = {
            1: 12,
            2: 12,
            3: 11,
            4: 10,
            5: 10,
            6: 9,
            7: 8,
        }
        return font_sizes.get(self._chart.rows, 8)

    @schema.apply("font")
    def title(self, *args, **kwargs):
        if args:
            label, *args = args
        else:
            label = kwargs.pop("label", None)
        label = titles.format(self, label)

        kwargs["fontsize"] = kwargs.pop("fontsize", self._default_fontsize)

        plt.sca(self.ax)
        return plt.title(label, *args, **kwargs)

    def legend(
        self,
        title="{variable_name} ({units})",
        orientation=None,
        location=None,
        **kwargs,
    ):
        if orientation and location:
            raise ValueError(
                "'orientation' and 'location' are mutually exclusive arguments"
            )
        elif orientation is not None:
            location = "right" if orientation == "vertical" else "bottom"
        elif location is None:
            # Default to a colorbar on the right
            location = "right"
        orientation = "vertical" if location in ("left", "right") else "horizontal"

        exclusive_layers = []
        for layer in self.layers:
            if layer._legend and layer.layer.cmap not in [
                lyr.cmap for lyr in exclusive_layers
            ]:
                exclusive_layers.append(layer.layer)
        cbars = [
            plt.colorbar(layer, orientation=orientation, **kwargs)
            for layer in exclusive_layers
        ]

        rotation = {"right": 270, "left": 90, "top": 0, "bottom": 0}[location]
        labelpad = {"right": 20, "left": -60, "top": -60, "bottom": 0}[location]
        for cbar in cbars:
            if title:
                cbar.set_label(
                    titles.format(self, title), rotation=rotation, labelpad=labelpad
                )

        if not any(key in kwargs for key in ("cax", "x", "y")):
            for cbar in cbars:
                cbar.auto = True
        for cbar in cbars:
            cbar.location = location
        self._chart._cbars = cbars
        return cbars

    def add_layer(self, method):
        def wrapper(data, *args, units=None, legend=True, **kwargs):
            values, points = self.domain.bbox(data)

            if units is not None:
                try:
                    import cf_units
                except ImportError:
                    raise ImportError("cf_units is required for unit conversion")
                values = cf_units.Unit(data.metadata("units")).convert(values, units)

            x = points["x"]
            y = points["y"]
            kwargs["transform"] = kwargs.pop("transform", data.crs())
            layer = method(x, y, values, *args, **kwargs)
            self.layers.append(DataLayer(data, layer, units=units, legend=legend))

        return wrapper

    @styles.guess
    def contour(self, *args, colors=None, **kwargs):
        if colors is not None:
            colors = styles.parse_colors(colors)
            kwargs.pop("cmap", None)
        return self.add_layer(self.ax.contour)(*args, **kwargs)

    @styles.guess
    def pcolormesh(self, *args, colors=None, **kwargs):
        if colors is not None:
            colors = styles.parse_colors(colors)
            kwargs.pop("cmap", None)
        return self.add_layer(self.ax.pcolormesh)(*args, **kwargs)

    @styles.guess
    @schema.apply("cmap")
    def contourf(self, *args, colors=None, transform_first=True, **kwargs):
        if colors is not None:
            colors = styles.parse_colors(colors)
            kwargs.pop("cmap", None)
        return self.add_layer(self.ax.contourf)(
            *args, colors=colors, transform_first=transform_first, **kwargs
        )

    shaded_contour = contourf


class Subplots:
    def __init__(self, chart):
        self._subplots = []
        self._chart = chart

    @property
    def subplots(self):
        if not self._subplots:
            self._chart.add_subplot()
        return self._subplots

    @property
    def layers(self):
        return [
            layer for layers in [subplot.layers for subplot in self] for layer in layers
        ]

    def add_subplot(self, subplot):
        self._subplots.append(subplot)

    def __len__(self):
        return len(self._subplots)

    def __getitem__(self, i):
        return self._subplots[i]

    def __getattr__(self, attr):
        if attr in Subplot.DATA_LAYER_METHODS:
            return self._data_layer(attr)
        try:
            methods = [getattr(subplot, attr) for subplot in self.subplots]
        except AttributeError:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{attr}'")

        def add_layer(*args, **kwargs):
            return [method(*args, **kwargs) for method in methods]

        return add_layer

    def titles(self, *args, **kwargs):
        return [subplot.title(*args, **kwargs) for subplot in self]

    def title(self, *args, **kwargs):
        if args:
            label, *args = args
        else:
            label = kwargs.pop("label", None)
        label = titles.format(self, label)

        if "y" not in kwargs:
            y1 = min(subplot.ax.get_position().y1 for subplot in self)
            kwargs["y"] = y1

        return self._chart.fig.suptitle(label, *args, **kwargs)

    def _data_layer(self, attr):
        def _iter_data(data, *args, **kwargs):
            if not hasattr(data, "__len__"):
                data = [data]
            if len(data) == 1 and self._subplots:
                data = [data[0]] * len(self._subplots)
            results = []
            for i, field in enumerate(data):
                if i + 1 > len(self._subplots):
                    subplot = self._chart.add_subplot(data=field)
                else:
                    subplot = self._subplots[i]
                result = getattr(subplot, attr)(field, *args, **kwargs)
                results.append(result)

            return results

        return _iter_data
