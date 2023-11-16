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


from earthkit.maps.styles.levels import Levels


class MagicsStyle:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @property
    def levels(self):
        selection_type = self.kwargs["contour_level_selection_type"]
        if selection_type == "list":
            return [float(i) for i in self.kwargs["contour_level_list"].split("/")]
        elif selection_type == "interval":
            return Levels(
                step=self.kwargs["contour_interval"],
                reference=self.kwargs.get("contour_reference_level"),
            )
        else:
            raise NotImplementedError(
                f"selection type '{selection_type}' is not yet supported"
            )
