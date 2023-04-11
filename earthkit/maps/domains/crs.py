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

DEFAULT_CRS = ccrs.PlateCarree()


def parse(crs):
    """
    Convert a string or dictionary representation of a CRS into a cartopy CRS.

    Parameters
    ----------
    crs : str, dict or cartopy.crs.CRS
        Some representation of a CRS to be parsed and converted into a cartopy
        CRS.
        If a string, must be the name of a cartopy CRS.
        If a dictionary, must include a "name" key matching the name of a
        cartopy CRS, plus and keyword arguments to be passed to the CRS
        constructor.

    Example
    -------
    >>> earthkit.maps.domains.parse_crs("PlateCarree")
    <Derived Projected CRS: +proj=eqc +ellps=WGS84 +a=6378137.0 +lon_0=0.0 +to ...>
    Name: unknown
    Axis Info [cartesian]:
    - E[east]: Easting (unknown)
    - N[north]: Northing (unknown)
    - h[up]: Ellipsoidal height (metre)
    Area of Use:
    - undefined
    Coordinate Operation:
    - name: unknown
    - method: Equidistant Cylindrical
    Datum: unknown
    - Ellipsoid: WGS 84
    - Prime Meridian: Greenwich
    >>> earthkit.maps.domains.parse_crs({"name": "PlateCarree", "central_longitude": 50})
    <Derived Projected CRS: +proj=eqc +ellps=WGS84 +a=6378137.0 +lon_0=50 +to_ ...>
    Name: unknown
    Axis Info [cartesian]:
    - E[east]: Easting (unknown)
    - N[north]: Northing (unknown)
    - h[up]: Ellipsoidal height (metre)
    Area of Use:
    - undefined
    Coordinate Operation:
    - name: unknown
    - method: Equidistant Cylindrical
    Datum: unknown
    - Ellipsoid: WGS 84
    - Prime Meridian: Greenwich

    Returns
    -------
    cartopy.crs.CRS
    """
    if crs is None:
        crs = DEFAULT_CRS

    if not isinstance(crs, ccrs.CRS):
        if isinstance(crs, dict):
            crs = from_dict(crs)
        else:
            crs = crs_from_string(crs)

    return crs


def from_dict(kwargs):
    """
    Convert a dictionary representation of a CRS into a cartopy CRS.

    Parameters
    ----------
    crs : dict
        A dictionary representation of a CRS to be parsed and converted into a
        cartopy CRS. Must include a "name" key matching the name of a cartopy
        CRS, plus and keyword arguments to be passed to the CRS constructor.

    Example
    -------
    >>> earthkit.maps.domains.parse_crs({"name": "PlateCarree", "central_longitude": 50})
    <Derived Projected CRS: +proj=eqc +ellps=WGS84 +a=6378137.0 +lon_0=50 +to_ ...>
    Name: unknown
    Axis Info [cartesian]:
    - E[east]: Easting (unknown)
    - N[north]: Northing (unknown)
    - h[up]: Ellipsoidal height (metre)
    Area of Use:
    - undefined
    Coordinate Operation:
    - name: unknown
    - method: Equidistant Cylindrical
    Datum: unknown
    - Ellipsoid: WGS 84
    - Prime Meridian: Greenwich

    Returns
    -------
    cartopy.crs.CRS
    """
    crs = crs_from_string(kwargs.pop("name")).__class__
    return crs(**kwargs)


def crs_from_string(string):
    """
    Convert a string name of a CRS into a cartopy CRS.

    Parameters
    ----------
    crs : dict
        A string matching the name of a cartopy CRS.

    Example
    -------
    >>> earthkit.maps.domains.parse_crs("PlateCarree")
    <Derived Projected CRS: +proj=eqc +ellps=WGS84 +a=6378137.0 +lon_0=0.0 +to ...>
    Name: unknown
    Axis Info [cartesian]:
    - E[east]: Easting (unknown)
    - N[north]: Northing (unknown)
    - h[up]: Ellipsoidal height (metre)
    Area of Use:
    - undefined
    Coordinate Operation:
    - name: unknown
    - method: Equidistant Cylindrical
    Datum: unknown
    - Ellipsoid: WGS 84
    - Prime Meridian: Greenwich

    Returns
    -------
    cartopy.crs.CRS
    """
    try:
        crs = getattr(ccrs, string)()
    except AttributeError:
        raise ValueError(f"cartopy has no CRS named '{string}'")
    return crs
