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

import inspect

import cartopy.crs as ccrs

GLOBE_AREA = 64800  # 360*180


class CRS:
    def to_ccrs(self, domain):
        return getattr(ccrs, self.cartopy_crs())(**self.get_kwargs(domain))

    def get_kwargs(self, domain):
        attributes = inspect.getmembers(
            self.__class__, lambda attr: not (inspect.isroutine(attr))
        )
        attributes = [
            attr
            for attr in attributes
            if not (attr[0].startswith("__") and attr[0].endswith("__"))
        ]
        return {attr[0].lower(): getattr(domain, attr[1]) for attr in attributes}

    def cartopy_crs(self):
        return self.__class__.__name__


class PlateCarree(CRS):
    CENTRAL_LONGITUDE = "central_lon"


class LambertAzimuthalEqualArea(CRS):
    CENTRAL_LATITUDE = "central_lat"
    CENTRAL_LONGITUDE = "central_lon"


class TransverseMercator(CRS):
    CENTRAL_LATITUDE = "central_lat"
    CENTRAL_LONGITUDE = "central_lon"


class AlbersEqualArea(CRS):
    CENTRAL_LATITUDE = "central_lat"
    CENTRAL_LONGITUDE = "central_lon"
    STANDARD_PARALLELS = "standard_parallels"


class NorthPolarStereo(CRS):
    CENTRAL_LONGITUDE = "central_lon"


class SouthPolarStereo(CRS):
    CENTRAL_LONGITUDE = "central_lon"


class Extents:

    CRS = PlateCarree

    def __init__(self, extents, small_threshold=0.2, large_threshold=0.6):
        self.extents = extents
        self.small_threshold = small_threshold * GLOBE_AREA
        self.large_threshold = large_threshold * GLOBE_AREA

    @property
    def area(self):
        if self.max_lat == self.min_lat:
            multiplicator = 2 * (90 - abs(self.max_lat))
        else:
            multiplicator = self.max_lat - self.min_lat

        return (self.max_lon - self.min_lon) * multiplicator

    @property
    def ratio(self):
        if self.min_lat == self.max_lat:
            denominator = 2 * (90 - abs(self.max_lat))
        else:
            denominator = self.max_lat - self.min_lat
        return (self.max_lon - self.min_lon) / denominator

    @property
    def standard_parallels(self):
        offset = (self.max_lat - self.min_lat) * (4 / 25)
        return (self.min_lat + offset, self.max_lat - offset)

    @property
    def min_lon(self):
        return self.extents[0]

    @property
    def max_lon(self):
        value = self.extents[1]
        if value < self.min_lon:
            value = 180 + (180 + value)
        return value

    @property
    def min_lat(self):
        return self.extents[2]

    @property
    def max_lat(self):
        return self.extents[3]

    @property
    def central_lat(self):
        return self.max_lat - (self.max_lat - self.min_lat) / 2

    @property
    def central_lon(self):
        return self.max_lon - (self.max_lon - self.min_lon) / 2

    def is_landscape(self):
        """Landscape domains are at leadt 20% wider than they are tall."""
        return self.ratio > 1.2

    def is_portrait(self):
        """Portrait domains are at least 20% taller than they are wide."""
        return self.ratio < 0.8

    def is_square(self):
        """Square domains have a width and height within 20% of each other."""
        return not self.is_landscape() and not self.is_portrait()

    def is_global(self):
        """Global domains cover > 60% of the globe."""
        return self.area > self.large_threshold

    def is_large(self):
        """Large domains cover < 60% of the globe but > 20%."""
        return not self.is_global() and self.area > self.small_threshold

    def is_small(self):
        """Small domains cover < 20% of the globe."""
        return not self.is_global() and not self.is_large()

    def is_polar(self):
        """Polar domains are centered around a pole."""
        return abs(self.central_lat) > 75

    def is_equatorial(self):
        """Equatorial domains are centered around the equator."""
        return abs(self.central_lat) < 25

    def mutate(self):
        return self

    def get_crs(self):
        return self.CRS().to_ccrs(self)


class Global(Extents):
    """A domain which covers >60% of the globe."""

    CRS = PlateCarree

    def mutate(self):
        if not self.is_global():
            return Equatorial(self.extents)
        return self


class Equatorial(Extents):
    """A domain with a central longitude < ±25 degrees, covering < 20% of the globe."""

    CRS = PlateCarree

    def mutate(self):
        if not self.is_equatorial():
            if self.is_polar():
                return NorthPolar(self.extents)
            else:
                return Square(self.extents)
        elif self.is_large():
            return LargeEqatorial(self.extents)
        return self


class NorthPolar(Extents):
    """A domain with a central longitude > 75 degrees."""

    CRS = NorthPolarStereo

    def mutate(self):
        if self.central_lat < 0:
            return SouthPolar(self.extents)
        return self


class SouthPolar(Extents):
    """A domain with a central longitude < -75 degrees."""

    CRS = SouthPolarStereo


class LargeEqatorial(Extents):
    """A domain with a central longitude < ±25 degrees, covering > 20% of the globe."""

    CRS = TransverseMercator


class Square(Extents):
    """A non-equitorial domain with an aspect ratio > 0.8 and < 1.2."""

    CRS = AlbersEqualArea

    def mutate(self):
        if self.is_landscape():
            return Landscape(self.extents)
        elif self.is_portrait():
            return Portrait(self.extents)
        return self


class Landscape(Extents):
    """A non-equitorial domain with an aspect ratio > 1.2."""

    CRS = AlbersEqualArea


class Portrait(Extents):
    """A non-equitorial domain with an aspect ratio < 0.8."""

    CRS = TransverseMercator


def crs_from_bounds(bounds):
    """
    Get an 'optimal' CRS to use for the given latitude and longitude extents.

    The method for choosing a CRS is as follows:
        - If the area of the map is greater than 60% of the globe, use a global
          equirectangular CRS.
        - If the central latitude is within ±25 degrees, use an equirectangular
          CRS.
        - If the central latitude is greater (less) than +(-)75 degrees, use a
          North (South) Polar Stereo CRS.
        - If the central latitude falls between ±25 and ±75 degrees and the
          aspect ratio is > 0.8, use an Albers Equal Area CRS.
        - If the central latitude falls between ±25 and ±75 degrees and the
          aspect ratio is < 0.8, use a Transverse Mercator CRS.

    This method is adapted from the method used by https://projectionwizard.org,
    which is discussed in the following article:
    Šavrič, B., Jenny, B. and Jenny, H. (2016). Projection Wizard – An online
    map projection selection tool. The Cartographic Journal, 53–2, p. 177–185.
    Doi: 10.1080/00087041.2015.1131938.

    Parameters
    ----------
    bounds : list
        The latitude and longitude extents of the bounding box, given as
        `[min_longitude, max_longitude, min_latitude, max_latitude]`.

    Returns
    -------
    cartopy.crs.CRS
    """
    domain = Global(bounds)
    while True:
        new_domain = domain.mutate()
        if new_domain == domain:
            break
        else:
            domain = new_domain
    return domain.get_crs()
