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


from earthkit.maps import styles

TEMPERATURE_AT_2M_IN_CELSIUS = styles.Contour(
    colors="turbo",
    extend="both",
    levels=range(-40, 41, 2),
    units="celsius",
)


TEMPERATURE_AT_2M_IN_KELVIN = styles.Contour(
    colors="turbo",
    extend="both",
    levels=range(230, 311, 2),
    units="K",
)


TEMPERATURE_AT_2M_IN_FAHRENHEIT = styles.Contour(
    colors="turbo",
    extend="both",
    levels=range(-40, 101, 5),
    units="fahrenheit",
)
