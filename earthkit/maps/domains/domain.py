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
import cv2
import numpy as np

from earthkit.maps import data, domains

DOMAIN_LOOKUP = data.load("domains")


NO_TRANSFORM_FIRST = [
    ccrs.Stereographic,
    ccrs.NearsidePerspective,
]


def force_minus_180_to_180(x):
    return (x + 180) % 360 - 180


def roll_from_0_360_to_minus_180_180(x):
    return np.argwhere(x[0] >= 180)[0][0]


def roll_from_minus_180_180_to_0_360(x):
    return np.argwhere(x[0] >= 0)[0][0]


def force_0_to_360(x):
    return x % 360


class Domain:
    @classmethod
    def from_string(cls, string, crs=None):
        from . import natural_earth

        domain_name = lookup_name(string)

        if crs is not None:
            crs = domains.crs.parse(crs)

        if domain_name is not None and domain_name in DOMAIN_LOOKUP["domains"]:
            domain_config = DOMAIN_LOOKUP["domains"][domain_name]
            if isinstance(domain_config, list):
                bounds = domain_config
                domain_crs = None
            else:
                bounds = domain_config.get("bounds")
                domain_crs = domain_config.get("crs")
            if crs is not None:
                bounds = domains.bounds.from_bbox(
                    bounds, crs, domains.crs.parse(domain_crs)
                )
            else:
                crs = domains.crs.parse(
                    domain_crs or domains.optimal.crs_from_bounds(bounds)
                )
                if domain_crs is None:
                    crs = domains.optimal.crs_from_bounds(bounds)
                    bounds = domains.bounds.from_bbox(bounds, crs)

        else:
            domain_name = domain_name or string
            source = natural_earth.NaturalEarthDomain(domain_name, crs)
            domain_name = source.domain_name
            bounds = source.bounds
            crs = source.crs
        return cls(bounds, crs, domain_name)

    @classmethod
    def from_data(cls, data):
        crs = data.projection().to_cartopy_crs()
        return cls(crs=crs)

    def __init__(self, bounds=None, crs=None, domain_name=None):
        if crs is None:
            if bounds is None:
                self.crs = crs
                self.bounds = bounds
            else:
                self.crs = domains.optimal.crs_from_bounds(bounds)
                self.bounds = domains.bounds.from_bbox(bounds, self.crs)
        else:
            self.crs = domains.crs.parse(crs)
            self.bounds = bounds

        self.domain_name = domain_name

    def __repr__(self):
        return self.title

    @property
    def _can_transform_first(self):
        return not any(isinstance(self.crs, crs) for crs in NO_TRANSFORM_FIRST)

    @property
    def title(self):
        if self.domain_name in DOMAIN_LOOKUP["the_countries"]:
            return f"the {self.domain_name}"
        elif self.domain_name is None:
            if self.bounds is None:
                string = "custom domain"
            else:
                ordinal_values = []
                for lon in self.latlon_bounds[:2]:
                    direction = ""
                    if lon != 0:
                        direction = "°W" if lon > 0 else "°E"
                    ordinal_values.append(f"{round(abs(lon), 2)}{direction}")
                for lat in self.latlon_bounds[2:]:
                    direction = ""
                    if lat != 0:
                        direction = "°N" if lat > 0 else "°S"
                    ordinal_values.append(f"{round(abs(lat), 2)}{direction}")
                string = ", ".join(ordinal_values)
            return string
        return self.domain_name

    @property
    def latlon_bounds(self):
        return domains.bounds.from_bbox(self.bounds, ccrs.PlateCarree(), self.crs)

    def bbox(self, field):
        from earthkit.maps.schemas import schema

        source_crs = field.projection().to_cartopy_crs()

        points = field.to_points(flatten=False)
        values = field.to_numpy(flatten=False)

        if self.bounds and schema.extract_domain:

            try:
                crs_bounds = domains.bounds.from_bbox(self.bounds, source_crs, self.crs)
            except NotImplementedError:
                pass
            else:
                roll_by = None
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

                kernel = np.ones((8, 8), dtype="uint8")
                bbox = cv2.dilate(bbox.astype("uint8"), kernel).astype(bool)

                shape = bbox[np.ix_(np.any(bbox, axis=1), np.any(bbox, axis=0))].shape

                points["x"] = points["x"][bbox].reshape(shape)
                points["y"] = points["y"][bbox].reshape(shape)
                values = values[bbox].reshape(shape)

        return values, points


def lookup_name(domain_name):
    """Format a domain name."""
    # normalise the input string and the lookup key
    domain_name = domain_name.lower().replace("_", " ")
    name_mapping = {k.lower(): k for k in DOMAIN_LOOKUP["domains"]}

    if domain_name not in name_mapping:
        for name, alt_names in DOMAIN_LOOKUP["alternate_names"].items():
            if domain_name in [alt_name.lower() for alt_name in alt_names]:
                domain_name = name
                break
        else:
            domain_name = None
    domain_name = name_mapping.get(domain_name, domain_name)

    return domain_name
