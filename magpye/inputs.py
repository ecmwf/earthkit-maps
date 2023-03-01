import emohawk
import numpy as np
import xarray as xr

from cartopy.util import add_cyclic_point

from magpye.domains import projections, auto
from magpye.schema import schema

X_RESOLUTION = 1000
Y_RESOLUTION = 1000


COMMON_VARIABLES = {
    "u": ["u", "u10"],
    "v": ["v", "v10"],
}


def find(values, candidates):
    for value in candidates:
        if value in values:
            break
    else:
        value = None
    return value


def get_data_var(data, variable):
    variable = find(data.data_vars, COMMON_VARIABLES[variable])
    if variable is None:
        raise ValueError(f"No data variable {variable} found")
    return variable


def extract_xy(
    data, x=None, y=None, src_crs=None, crs=None, bounds=None, data_vars=None
):
    data = emohawk.open(data)

    dataset = xr.Dataset(data.to_xarray()).squeeze()
    data = emohawk.open(dataset)

    # if bounds is not None:
    #     crs_bounds = auto.get_crs_extents(bounds, src_crs, crs)
    #     dataset = xr.Dataset(data.to_xarray()).squeeze()
    #     dataset.coords[data.axis("x").name] = (dataset.coords[data.axis("x").name] + 180) % 360 - 180
    #     dataset = dataset.sortby(getattr(dataset, data.axis("x").name))

    #     dataset = dataset.sel(
    #         **{
    #             data.axis("x").name: slice(*crs_bounds[:2]),
    #             data.axis("y").name: slice(*crs_bounds[2:]),
    #         }
    #     )

    #     data = emohawk.open(dataset)

    x_values = _extract_axis(data, x=x)
    y_values = _extract_axis(data, y=y)

    dataset = xr.Dataset(data.to_xarray()).squeeze()
    if data_vars is None:
        data_values = [dataset[list(dataset.data_vars)[0]].values]
    else:
        data_values = [dataset[get_data_var(dataset, var)].values for var in data_vars]

    try:
        for i, item in enumerate(data_values):
            data_values[i], x_values = add_cyclic_point(item, coord=x_values)
    except:  # noqa: E722
        # TODO: Decide what to do with un-cyclifiable data
        pass

    if len(data_values) == 1:
        data_values = data_values[0]

    return data_values, x_values, y_values


def _extract_axis(data, **kwargs):
    axis_name, axis_value = list(kwargs.items())[0]

    if axis_value is None:
        values = data.axis(axis_name).values
    else:
        values = data.to_xarray()[axis_value].values

    return values


def extract(data_vars=None):
    def wrapper(method):
        def sanitised_method(self, data, *args, x=None, y=None, **kwargs):
            crs = projections.get_crs(data)

            if self._domain and not self._bounds:
                bounds = self.bounds
                chart_crs = self.crs
            else:
                bounds = self._bounds
                chart_crs = self._crs

            data, x, y = extract_xy(
                data, x, y, crs, chart_crs, bounds, data_vars=data_vars
            )

            if self._bounds is None and self._crs is None and self._domain is None:
                self._crs = crs

            self._setup_domain()
            kwargs["transform"] = kwargs.get("transform", crs)

            return method(self, data, *args, x=x, y=y, **kwargs)

        return sanitised_method

    return wrapper
