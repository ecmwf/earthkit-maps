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


from earthkit.data import remote_shp

RESOLUTIONS = {
    "low": "60m",
    "medium": "20m",
    "high": "10m",
    "very high": "03m",
}


EUROSTAT_URL = (
    "https://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/"
    "ref-nuts-{year}-{resolution}.shp.zip"
)


def NUTS(self, level=0, resolution="medium", year=2021):
    """Get NUTS regions."""
    resolution = RESOLUTIONS[resolution]
    url = EUROSTAT_URL.format(year=year, resolution=resolution)
    name = f"nuts-level{level}-{year}-{resolution}"
    path = remote_shp("nuts", name, url)
    return path
