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


import glob
import importlib

import yaml

from earthkit.maps import definitions, styles
from earthkit.maps.layers.metadata import compare_units


def suggest_style(data, units=None):
    for fname in glob.glob(str(definitions.DATA_DIR / "identities" / "*")):
        with open(fname, "r") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
        for criteria in config["criteria"]:
            for key, value in criteria.items():
                if data.metadata(key, default=None) != value:
                    break
            else:
                break
        else:
            continue
        break
    else:
        return styles.DEFAULT_STYLE

    if units is None:
        style = config["styles"]["default"]
    else:
        for unit, style in config["styles"].get("units", {}).items():
            if compare_units(unit, units):
                break
        else:
            raise ValueError(f"{config['id']} has no styles with units {units}")

    module, style = style.split(".")

    module = importlib.import_module(f"earthkit.maps.styles.{module}")

    return getattr(module, style)
