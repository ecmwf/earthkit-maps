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

from earthkit.maps.charts import Chart


class Subplots(Chart):
    def __init__(self, *args, rows=None, cols=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._rows = rows
        self._cols = cols

    @property
    def ax(self):
        if self._ax is None:
            self._ax = self.fig.add_subplot(
                self._rows, self._cols, 1, projection=self.crs
            )
            if self.bounds is not None:
                self._ax.set_extent(self.bounds, crs=self.crs)
        return self._ax
