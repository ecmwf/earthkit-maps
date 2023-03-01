import warnings

import cartopy.crs as ccrs
import emohawk
import pyproj
import xarray as xr

PROJ4_CRS = {
    "laea": {
        "crs": ccrs.LambertAzimuthalEqualArea,
        "kwargs": {
            "central_longitude": "lon_0",
            "central_latitude": "lat_0",
            "false_easting": "x_0",
            "false_northing": "y_0",
        },
    }
}


def proj4_to_ccrs(proj4_string):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        params = pyproj.CRS.from_proj4(proj4_string).to_dict()

    ccrs_setup = PROJ4_CRS[params["proj"]]
    crs = ccrs_setup["crs"]
    kwargs = ccrs_setup["kwargs"]

    return crs(**{kwarg: params[kwargs[kwarg]] for kwarg in kwargs})


def get_crs(data):
    data = xr.Dataset(emohawk.open(data).to_xarray())
    var = list(data.data_vars)[0]

    proj4_string = None
    if "proj4_string" in data[var].attrs:
        proj4_string = data[var].attrs["proj4_string"]
    elif "grid_mapping" in data[var].attrs:
        proj4_string = data[data[var].attrs["grid_mapping"]].attrs["proj4_params"]

    if proj4_string is not None:
        crs = proj4_to_ccrs(proj4_string)
    else:
        crs = ccrs.PlateCarree()

    return crs