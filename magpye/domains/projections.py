import warnings

import cartopy.crs as ccrs
import pyproj



FIXED_CRSS = ["NorthPolarStereo", "SouthPolarStereo"]


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

def proj_to_ccrs(proj4_string):
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        params = pyproj.CRS.from_proj4(proj4_string).to_dict()

    ccrs_setup = PROJ4_CRS[params["proj"]]
    crs = ccrs_setup["crs"]
    kwargs = ccrs_setup["kwargs"]

    return crs(**{kwarg: params[kwargs[kwarg]] for kwarg in kwargs})
