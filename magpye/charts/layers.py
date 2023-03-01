

class DataLayer:

    from .legends import legend

    def __init__(self, data, layer, legend=None):
        self.data = data
        self.layer = layer
        self._legend = legend
        self._legend_location = None
        self._legend_ax = None


def append(method):
    def wrapper(self, data, *args, legend=True, **kwargs):
        layer = method(self, data, *args, **kwargs)
        self._layers.append(DataLayer(data, layer, legend))
        self._release_queue()
        return layer

    return wrapper
