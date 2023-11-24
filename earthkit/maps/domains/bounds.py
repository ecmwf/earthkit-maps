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
import numpy as np

CYCLIC_SYSTEMS = ["PlateCarree", "Mercator"]


def from_geometry(geom, crs=None):
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


def from_bbox(extents, crs, src_crs=None):
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
    # TODO: Implement bbox conversion for stereographic projections
    if isinstance(src_crs, ccrs.Stereographic):
        raise NotImplementedError(f"cannot convert bbox for CRS {src_crs}")

    if src_crs is None:
        src_crs = ccrs.PlateCarree()

    # Check if extents are an earthkit-data BoundingBox
    if hasattr(extents, "north"):
        extents = [extents.west, extents.east, extents.south, extents.north]

    ll_grid = crs.__class__.__name__ in CYCLIC_SYSTEMS

    min_lon, max_lon, min_lat, max_lat = extents
    mid_lon = max_lon - (max_lon - min_lon) / 2

    corners = [
        crs.transform_point(min_lon, min_lat, src_crs),
        crs.transform_point(min_lon, max_lat, src_crs),
        crs.transform_point(max_lon, max_lat, src_crs),
        crs.transform_point(max_lon, min_lat, src_crs),
    ]

    min_x = min([corner[0] for corner in corners[:2]])
    max_x = max([corner[0] for corner in corners[2:4]])
    min_y = min([corner[1] for corner in [corners[0], corners[-1]]])
    max_y = max([corner[1] for corner in corners[1:3]])

    if ll_grid and (
        (abs(corners[2][0] - corners[3][0]) > 180)
        or (abs(corners[0][0] - corners[1][0]) > 180)
    ):
        min_x = min([corner[0] % 360 for corner in corners[:2]])
        max_x = max([corner[0] % 360 for corner in corners[2:4]])

    mid_bottom = crs.transform_point(mid_lon, min_lat, src_crs)
    mid_top = crs.transform_point(mid_lon, max_lat, src_crs)

    min_y = min(min_y, mid_bottom[1])
    max_y = max(max_y, mid_top[1])

    if min_x > max_x and ll_grid:
        min_x %= 360
        max_x %= 360

    return [min_x, max_x, min_y, max_y]


def to_string(bounds):
    """
    Convert a list of lat-lon bounds to a human-readable string.

    Parameters
    ----------
    bounds : list
        A list of latitude-longitude bounds in the order
        [min_lon, max_lon, min_lat, max_lat].

    Returns
    -------
    str
    """
    ordinal_values = []
    for lon in bounds[:2]:
        direction = ""
        if lon != 0:
            direction = "°W" if lon > 0 else "°E"
        ordinal_values.append(f"{round(abs(lon), 2)}{direction}")
    for lat in bounds[2:]:
        direction = ""
        if lat != 0:
            direction = "°N" if lat > 0 else "°S"
        ordinal_values.append(f"{round(abs(lat), 2)}{direction}")

    return ", ".join(ordinal_values)
