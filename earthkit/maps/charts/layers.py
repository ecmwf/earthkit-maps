
import matplotlib.pyplot as plt

from . import titles, styles
from earthkit.maps import domains, sources
from earthkit.maps.schema import schema


class DataLayer:
    
    def __init__(self, data, layer, legend=None):
        self.data = data
        self.layer = layer
        self._legend = legend
        self._legend_location = None
        self._legend_ax = None


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
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute '{attr}'")
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
    
    def legend(self, **kwargs):
        exclusive_layers = []
        for layer in self.layers:
            if layer._legend and layer.layer.cmap not in [l.cmap for l in exclusive_layers]:
                exclusive_layers.append(layer.layer)
        return [plt.colorbar(layer, **kwargs) for layer in exclusive_layers]
    
    def add_layer(self, method):
        def wrapper(data, *args, legend=True, **kwargs):
            values, points = self.domain.bbox(data)
            x = points["lon"]
            y = points["lat"]
            kwargs["transform"] = kwargs.pop("transform", data.crs())
            layer = method(x, y, values, *args, **kwargs)
            self.layers.append(DataLayer(data, layer, legend=legend))
        return wrapper

    def contour(self, *args, **kwargs):
        return self.add_layer(self.ax.contour)(*args, **kwargs)

    @schema.apply("cmap")
    def contourf(self, *args, colors=None, transform_first=True, **kwargs):
        if colors is not None:
            colors = styles.parse_colors(colors)
            kwargs.pop("cmap", None)
        return self.add_layer(self.ax.contourf)(
            *args, colors=colors, transform_first=transform_first, **kwargs
        )
    

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
        return [layer for layers in [subplot.layers for subplot in self] for layer in layers]
    
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
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute '{attr}'")
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

        return self._chart.fig.suptitle(label, *args, **kwargs)
    
    def _data_layer(self, attr):
        def _iter_data(data, *args, **kwargs):            
            if not hasattr(data, "__len__"):
                data = [data]
            if len(data) == 1 and self._subplots:
                data = [data[0]]*len(self._subplots)
            results = []
            for i, field in enumerate(data):
                if i+1 > len(self._subplots):
                    subplot = self._chart.add_subplot(data=field)
                else:
                    subplot = self._subplots[i]
                result = getattr(subplot, attr)(field, *args, **kwargs)
                results.append(result)
            
            return results
        return _iter_data