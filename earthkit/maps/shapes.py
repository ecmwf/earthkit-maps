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


import earthkit.data


def NUTS(level=0, year=2021, resolution="60M"):
    from earthkit.data.testing import earthkit_remote_test_data_file

    remote_nuts_url = earthkit_remote_test_data_file(
        "test-data",
        f"NUTS_RG_{resolution}_{year}_4326_LEVL_{level}.geojson",
    )
    return earthkit.data.from_source("url", remote_nuts_url)
