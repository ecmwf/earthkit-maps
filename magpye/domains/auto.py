import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import numpy as np

from magpye import _data
from magpye.domains import parse_crs
from magpye.schema import schema

from . import _crs

GLOBE_AREA = 64800  # 360*180
NATURAL_EARTH_SOURCES = {
    "admin_0_map_units": "NAME_LONG",
    "admin_0_countries": "NAME_LONG",
    "admin_1_states_provinces": "name_en",
}


class Extents:

    CRS = _crs.PlateCarree

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
        return self.extents[1]

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
        return self.ratio > 1.2

    def is_portrait(self):
        return self.ratio < 0.8

    def is_square(self):
        return not self.is_landscape() and not self.is_portrait()

    def is_global(self):
        return self.area > self.large_threshold

    def is_large(self):
        return not self.is_global() and self.area > self.small_threshold

    def is_small(self):
        return not self.is_global() and not self.is_large()

    def is_polar(self):
        return abs(self.central_lat) > 75

    def is_equatorial(self):
        return abs(self.central_lat) < 25

    def mutate(self):
        return self

    def get_crs(self):
        return self.CRS().to_ccrs(self)


class Global(Extents):
    """A domain which covers >60% of the globe."""

    CRS = _crs.PlateCarree

    def mutate(self):
        if not self.is_global():
            return Equatorial(self.extents)
        return self


class Equatorial(Extents):
    """A domain with a central longitude < ±25 degrees, covering < 20% of the globe."""

    CRS = _crs.PlateCarree

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

    CRS = _crs.NorthPolarStereo

    def mutate(self):
        if self.central_lat < 0:
            return SouthPolar(self.extents)
        return self


class SouthPolar(Extents):
    """A domain with a central longitude < -75 degrees."""

    CRS = _crs.SouthPolarStereo


class LargeEqatorial(Extents):
    """A domain with a central longitude < ±25 degrees, covering > 20% of the globe."""

    CRS = _crs.TransverseMercator


class Square(Extents):
    """A non-equitorial domain with an aspect ratio > 0.8 and < 1.2."""

    CRS = _crs.AlbersEqualArea

    def mutate(self):
        if self.is_landscape():
            return Landscape(self.extents)
        elif self.is_portrait():
            return Portrait(self.extents)
        return self


class Landscape(Extents):
    """A non-equitorial domain with an aspect ratio > 1.2."""

    CRS = _crs.AlbersEqualArea


class Portrait(Extents):
    """A non-equitorial domain with an aspect ratio < 0.8."""

    CRS = _crs.TransverseMercator


def get_optimal_crs(extents):
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
    extents : list
        The latitude and longitude extents of the bounding box, given as
        `[min_longitude, max_longitude, min_latitude, max_latitude]`.

    Returns
    -------
    cartopy.crs.CRS
    """
    domain = Global(extents)
    while True:
        new_domain = domain.mutate()
        if new_domain == domain:
            break
        else:
            domain = new_domain
    return domain.get_crs()


def get_crs_extents(extents, crs, src_crs=None):
    """
    Get a bounding box which entirely contains another box from a different CRS.

    Parameters
    ----------
    extents : list
        The x and y extents of the bounding box on the `src_crs`, given as
        `[min_x, max_x, min_y, max_y]`.
    crs : cartopy.crs.CRS
        The coordinate reference system in which to generate a new bounding box
        which entriely contains the given extents.
    src_crs : cartopy.crs.CRS (optional)
        The coordinate reference system on which the extents are defined. If not
        passed, an equirectangular CRS will be assumed, with extents defined as
        latitudes and longitudes.

    Returns
    -------
    list
    """
    if src_crs is None:
        src_crs = schema.reference_crs
    min_lon, max_lon, min_lat, max_lat = extents
    corners = [
        crs.transform_point(min_lon, min_lat, src_crs),
        crs.transform_point(min_lon, max_lat, src_crs),
        crs.transform_point(max_lon, max_lat, src_crs),
        crs.transform_point(max_lon, min_lat, src_crs),
    ]

    min_x = min([corner[0] for corner in corners])
    max_x = max([corner[0] for corner in corners])
    min_y = min([corner[1] for corner in corners])
    max_y = max([corner[1] for corner in corners])
    mid_x = max_x - (max_x - min_x) / 2

    mid_bottom = src_crs.transform_point(mid_x, min_y, crs)
    mid_top = src_crs.transform_point(mid_x, max_y, crs)

    min_y = min(min_y, mid_bottom[1])
    max_y = max(max_y, mid_top[1])

    return [min_x, max_x, min_y, max_y]


def get_bounds(geom, crs=None):
    """
    Get a bounding box around a geometry on a given coordinate reference system.

    Parameters
    ----------
    geom : shapely.geometry
        A shapely geometry around which the bounding box should be drawn.
    crs : cartopy.crs.CRS
        The coordinate reference system in which to generate a new bounding box
        which entriely contains the given geometry.

    Returns
    -------
    list
    """
    try:
        geoms = geom.geoms
    except AttributeError:
        geoms = [geom]
    iterator = list(geoms)

    x = np.concatenate([g.boundary.xy[0] for g in iterator])
    y = np.concatenate([g.boundary.xy[1] for g in iterator])

    if crs is not None:
        xy = crs.transform_points(x=x, y=y, src_crs=ccrs.PlateCarree())
        x = [point[0] for point in xy]
        y = [point[1] for point in xy]
    elif any(lon in (min(x), max(x)) for lon in (-180, 180)):
        x = [v % 360 for v in x]

    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)

    return [xmin, xmax, ymin, ymax]


def get_domain_extents_and_crs(domain, crs=None, padding=0.1):
    """
    Get an optimal bounding box and CRS for a named domain.

    Parameters
    ----------
    domain : str
        The name of the domain for which get bounds and a CRS. Can be the name
        of any country, state or province included in Natural Earth's
        administrative regions shapefiles, or one of magpye's built-in preset
        domains.
    crs : cartopy.crs.CRS
        The coordinate reference system in which to generate the bounding box
        for the given domain. This will therefore be the CRS returned.
    padding: float
        The extra space around the edges of the given domain to include, so as
        to ensure the full domain is visible. Note that this has no effect on
        magpye preset domains, and will only work for named countries and
        provinces.

    Returns
    -------
    (list, cartopy.crs.CRS)
    """
    lookup = _data.load("domains")
    domains = {dom.lower(): lookup["domains"][dom] for dom in lookup["domains"]}
    key = domain.lower().replace("_", " ")

    config = None
    if key not in domains:
        for dom, alts in lookup.get("alternate_names", dict()).items():
            if key in [alt.lower() for alt in alts]:
                key = dom.lower()
    config = domains.get(key)

    bounds = None
    domain_crs = None
    if config is not None:
        if isinstance(config, list):
            bounds = config
        else:
            bounds = config.get("bounds")
            domain_crs = config.get("crs")
        if crs is not None:
            bounds = get_crs_extents(bounds, crs, domain_crs)
        else:
            crs = parse_crs(domain_crs or get_optimal_crs(bounds))
            crs_bounds = bounds
            if domain_crs is None:
                crs = get_optimal_crs(bounds)
                crs_bounds = get_crs_extents(bounds, crs)

    else:
        for source, attribute in NATURAL_EARTH_SOURCES.items():
            shpfilename = shpreader.natural_earth(
                resolution="110m", category="cultural", name=source
            )
            reader = shpreader.Reader(shpfilename)
            for record in reader.records():
                name = record.attributes.get(attribute) or ""
                name = name.replace("\x00", "")
                if name.lower() == key:
                    break
            else:
                continue
            break
        else:
            raise ValueError(f"Could not find bounds for '{domain}'")
        bounds = get_bounds(record.geometry)
        crs = crs or get_optimal_crs(bounds)
        crs_bounds = get_bounds(record.geometry, crs=crs)

        if padding:
            x_offset = (crs_bounds[1] - crs_bounds[0]) * padding
            y_offset = (crs_bounds[3] - crs_bounds[2]) * padding
            offset = min(x_offset, y_offset)
            crs_bounds = [
                crs_bounds[0] - offset,
                crs_bounds[1] + offset,
                crs_bounds[2] - offset,
                crs_bounds[3] + offset,
            ]

    return crs_bounds, crs
