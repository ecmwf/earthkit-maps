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

import cartopy.crs as ccrs
import earthkit.data
import numpy as np
from cartopy.util import add_cyclic_point

from earthkit.maps import styles
from earthkit.maps.schemas import schema

_NO_EARTHKIT_REGRID = False
try:
    import earthkit.regrid
except ImportError:
    _NO_EARTHKIT_REGRID = True


class Input:
    """
    Class for managing input data for charts.
    """

    def __init__(
        self, data, x=None, y=None, transform=None, style=None, domain=None, **kwargs
    ):
        self._data = data
        self._transform = transform

        self._converted_values = None

        self._style = style
        self._kwargs = kwargs

        self.x = x
        self.y = y
        self._values = None
        self.extract(domain)

    @property
    def data(self):
        if not isinstance(self._data, (earthkit.data.core.Base, list, np.ndarray)):
            self._data = earthkit.data.from_object(self._data)
        if isinstance(self._data, earthkit.data.core.Base) and hasattr(
            self._data, "__len__"
        ):
            try:
                self._data = self._data[0]
            except (ValueError, TypeError, AttributeError):
                pass
        return self._data

    @property
    def source_units(self):
        try:
            units = self._data.metadata("units", default=None)
        except (NotImplementedError, AttributeError):
            units = None
        return units

    @property
    def short_name(self):
        try:
            short_name = self._data.metadata("short_name", default="")
        except (NotImplementedError, AttributeError):
            short_name = ""
        return short_name

    @property
    def transform(self):
        if self._transform is None:
            try:
                self._transform = self._data.projection().to_cartopy_crs()
            except AttributeError:
                self._transform = ccrs.PlateCarree()
        return self._transform

    @property
    def style(self):
        if self._style is None:
            style_units = None
            if not schema.use_preferred_styles:
                style_units = self._kwargs.pop("units", None) or self.source_units
            self._style = styles.auto.guess_style(self.data, units=style_units)
        return self._style

    @property
    def values(self):
        return self.style.convert_units(
            self._values,
            self.source_units,
            self.short_name,
        )

    @property
    def gridspec(self):
        if self.data.metadata("gridType", default="") == "reduced_gg":
            n = self.data.metadata("N", default=None)
            if n is not None:
                if self.data.metadata("isOctahedral", default=0):
                    g = f"O{n}"
                else:
                    g = f"N{n}"
            return {"grid": g}
        elif self.data.metadata("gridType", default="") == "healpix":
            n = self.data.metadata("Nside", default=None)
            o = self.data.metadata("orderingConvention", default=None)
            if n is not None and o is not None:
                return {"grid": f"H{n}", "ordering": o}

    def extract(self, domain=None):
        if self.x is None and self.y is None:

            if self.gridspec is not None:
                if _NO_EARTHKIT_REGRID:
                    raise ImportError(
                        f"earthkit-regrid is required for plotting data on a"
                        f"'{self.gridspec['grid']}' grid"
                    )
                points = get_points(schema.interpolate_target_resolution)
                self._values = earthkit.regrid.interpolate(
                    self.data.values,
                    self.gridspec,
                    {
                        "grid": [
                            schema.interpolate_target_resolution,
                            schema.interpolate_target_resolution,
                        ],
                    },
                )
                if domain is not None:
                    self._values, points = domain.latlon_bbox(self._values, points)
            else:
                if domain is None:
                    self._values = self.data.to_numpy(flatten=False)
                    points = self.data.to_points(flatten=False)
                else:
                    self._values, points = domain.bbox(self.data)
            self.y = points["y"]
            self.x = points["x"]

        elif self._values is None:
            try:
                self._values = self.data.values()
            except AttributeError:
                self._values = self.data

        if np.all(self.x[:-1] == self.x[1:]):
            self.y = self.y[:, 0]
            self._values, self.x = add_cyclic_point(self._values, coord=self.x[0])
            self.x, self.y = np.meshgrid(self.x, self.y)


class Vector(Input):
    def __init__(self, u, v, *args, **kwargs):
        self._u_data = u
        self._v_data = v
        self.u = None
        self.v = None
        super().__init__(u, *args, **kwargs)

    def extract(self, domain):
        self._data = self._u_data
        super().extract(domain)
        self.u = self._values
        self.x, self.y = None, None

        self._data = self._v_data
        super().extract(domain)
        self.v = self._values

        self._values = [self.u, self.v]


def get_points(dx):
    import numpy as np

    lat_v = np.linspace(90, -90, int(180 / dx) + 1)
    lon_v = np.linspace(0, 360 - dx, int(360 / dx))
    lon, lat = np.meshgrid(lon_v, lat_v)
    return {"x": lon, "y": lat}


def sanitise(data):
    if not isinstance(data, (earthkit.data.core.Base, list, np.ndarray)):
        data = earthkit.data.from_object(data)
    if not isinstance(data, earthkit.data.core.Base) or not hasattr(data, "__len__"):
        data = [data]
    return data[0]
