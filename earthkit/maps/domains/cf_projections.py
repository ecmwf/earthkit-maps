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
