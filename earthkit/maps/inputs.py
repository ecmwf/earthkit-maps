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

import warnings

import cartopy.crs as ccrs
import cv2
import emohawk
import numpy as np

from earthkit.maps import domains
from earthkit.maps.schema import schema

# from cartopy.util import add_cyclic_point


X_RESOLUTION = 1000
Y_RESOLUTION = 1000

DEFAULT_PROJ = ccrs.PlateCarree()

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


def force_minus_180_to_180(x):
    return (x + 180) % 360 - 180


def roll_from_0_360_to_minus_180_180(x):
    return np.argwhere(x[0] >= 180)[0][0]


def roll_from_minus_180_180_to_0_360(x):
    return np.argwhere(x[0] >= 0)[0][0]


def force_0_to_360(x):
    return x % 360


def extract_xy(
    field, x=None, y=None, src_crs=None, crs=None, bounds=None, data_vars=None
):
    points = field.to_points(flatten=False)
    values = field.to_numpy(flatten=False)

    if (
        bounds is not None
        and crs.__class__.__name__ not in domains.projections.FIXED_CRSS
    ):
        crs_bounds = domains.bounds.from_bbox(bounds, src_crs, crs)

        roll_by = None
        if src_crs.__class__.__name__ in domains.bounds.CYCLIC_SYSTEMS:
            if crs_bounds[0] < 0 and crs_bounds[1] > 0:
                if crs_bounds[0] < points["x"].min():
                    roll_by = roll_from_0_360_to_minus_180_180(points["x"])
                    points["x"] = force_minus_180_to_180(points["x"])
                    for i in range(2):
                        crs_bounds[i] = force_minus_180_to_180(crs_bounds[i])
            elif crs_bounds[0] < 180 and crs_bounds[1] > 180:
                if crs_bounds[1] > points["x"].max():
                    roll_by = roll_from_minus_180_180_to_0_360(points["x"])
                    points["x"] = force_0_to_360(points["x"])
                    for i in range(2):
                        crs_bounds[i] = force_0_to_360(crs_bounds[i])
        if roll_by is not None:
            points["x"] = np.roll(points["x"], roll_by, axis=1)
            points["y"] = np.roll(points["y"], roll_by, axis=1)
            values = np.roll(values, roll_by, axis=1)

        bbox = np.where(
            (points["x"] >= crs_bounds[0])
            & (points["x"] <= crs_bounds[1])
            & (points["y"] >= crs_bounds[2])
            & (points["y"] <= crs_bounds[3]),
            True,
            False,
        )

        kernel = np.ones((3, 3), dtype="uint8")
        bbox = cv2.dilate(bbox.astype("uint8"), kernel).astype(bool)

        shape = bbox[np.ix_(np.any(bbox, axis=1), np.any(bbox, axis=0))].shape

        points["x"] = points["x"][bbox].reshape(shape)
        points["y"] = points["y"][bbox].reshape(shape)
        values = values[bbox].reshape(shape)

    # try:
    #     for i, item in enumerate(values):
    #         values[i], points["x"] = add_cyclic_point(item, coord=points["x"])
    # except:  # noqa: E722
    #     # TODO: Decide what to do with un-cyclifiable data
    #     pass

    return values, points["x"], points["y"]


def _extract_axis(data, **kwargs):
    axis_name, axis_value = list(kwargs.items())[0]

    if axis_value is None:
        values = data.axis(axis_name).values
    else:
        values = data.to_xarray()[axis_value].values

    return values


def extract(data_vars=None):
    def wrapper(method):
        def sanitised_method(self, fields, *args, x=None, y=None, **kwargs):

            if not isinstance(fields, emohawk.sources.file.File):
                fields = [fields]

            # TODO: iteration over fields
            for field in fields[:1]:

                try:
                    proj_string = field.to_proj()[0]
                except AttributeError as err:
                    warnings.warn(f"{err}; assuming {schema.reference_crs} CRS")
                    crs = domains.crs.parse(schema.reference_crs)
                else:
                    if proj_string is None:
                        crs = domains.crs.parse(schema.reference_crs)
                    else:
                        crs = domains.projections.proj_to_ccrs(proj_string)

                if self._domain is None:
                    self._domain = domains.Domain(crs=crs)

                values, x, y = extract_xy(
                    field, x, y, crs, self.crs, self.bounds, data_vars=data_vars
                )

                kwargs["transform"] = kwargs.get("transform", crs)

                return method(self, values, *args, x=x, y=y, **kwargs)

        return sanitised_method

    return wrapper
