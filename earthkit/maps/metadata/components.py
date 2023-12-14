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


COMPONENTS = {
    "u": {
        "criteria": [
            {"short_name": "10u"},
            {"short_name": "100u"},
            {"short_name": "u"},
            {"long_name": "10 metre U wind component"},
            {"variable": "u10"},
        ],
        "counterpart": "v",
    },
    "v": {
        "criteria": [
            {"short_name": "10v"},
            {"short_name": "100v"},
            {"short_name": "v"},
            {"long_name": "10 metre V wind component"},
            {"variable": "v10"},
        ],
        "counterpart": "u",
    },
}


def extract(data, components):
    results = []
    for component in components:
        for criteria in COMPONENTS[component]["criteria"]:
            for key, value in criteria.items():
                if value in data.metadata(key, default=None):
                    break
            else:
                continue
            break
        else:
            raise KeyError(f"No component '{component}' found in data")
        results.append(data.sel(**{key: value}))

    return results
