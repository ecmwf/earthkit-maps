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

import emohawk


class DataLayer:

    from .legends import legend

    def __init__(self, data, layer, legend=None):
        self.data = data
        self.layer = layer
        self._legend = legend
        self._legend_location = None
        self._legend_ax = None


def append(method):
    def wrapper(self, data, *args, legend=True, **kwargs):
        if isinstance(data, str):
            data = emohawk.from_source("file", data)
        layer = method(self, data, *args, **kwargs)
        self._layers.append(DataLayer(data, layer, legend))
        self._release_queue()
        return layer

    return wrapper
