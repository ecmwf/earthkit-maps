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


class Input:
    """
    Class for managing input data for charts.
    """

    def __init__(
        self, data, x=None, y=None, transform=None, style=None, domain=None, **kwargs
    ):
        self._data = data
        self._transform = transform

        self.x = x
        self.y = y
        self._values = None
        self.extract_scalar(domain)

        self._converted_values = None

        self._style = style
        self._kwargs = kwargs

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

    def extract_scalar(self, domain=None):
        if self.x is None and self.y is None:

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
