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

import os
from functools import partial

import cartopy
import yaml

from earthkit.maps import definitions

READERS = {
    ".yaml": partial(yaml.load, Loader=yaml.SafeLoader),
}


class DataNotFoundError(FileNotFoundError):
    pass


class AmbiguousDataError(Exception):
    pass


def load(source, data_type=None):
    """
    Load an earthkit.maps auxilliary data file.

    Parameters
    ----------
    source : str
        The name of a file (with or without extension) found within magpye/data.
    data_type : str
        If applicable, the name of the subdirectory withing magpye/data in which
        the auxilliary file will be found.
    """
    path = definitions.DATA_DIR
    if data_type is not None:
        path /= data_type

    matches = list(path.glob(f"{source}*"))
    if not matches:
        raise DataNotFoundError(f"could not find data named '{source}'")
    elif len(matches) > 1:
        raise AmbiguousDataError(
            f"multiple data sources named '{source}'; file extension required"
        )

    path = matches[0]
    reader = READERS.get(path.suffix)
    if reader is None:
        raise KeyError(f"no reader for file with extension {path.suffix}")

    with open(path, "r") as f:
        return reader(f)


def remote_shp(namespace, name, url):
    data_dir = os.path.join(cartopy.config["data_dir"], "shapefiles", namespace)

    file_path = os.path.join(data_dir, f"{name}.shp")

    if not os.path.exists(file_path):
        os.makedirs(data_dir, exist_ok=True)

    return file_path
