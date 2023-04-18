
from earthkit.maps import domains
from earthkit.maps.charts import layers


def matplotlibify(method):
    def deconstruct(self, field, *args, **kwargs):
        crs = field.crs()
        if self.domain is None:
            domain = domains.Domain(crs=crs)
        else:
            domain = self.domain
        values, points = domain.bbox(field)
        x = points["lon"]
        y = points["lat"]
        transform = kwargs.pop("transform", crs)
        
        return getattr(plot_ax, method.__name__)(
            x, y, values, *args, transform=transform, **kwargs
        )
    return deconstruct

