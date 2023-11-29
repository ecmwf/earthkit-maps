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
    colors=[
        (0, 0, 0.5),
        (0, 0, 0.5),
        (0, 0, 0.5),
        (0, 0, 0.5),
        (0, 0, 0.85),
        (0.25, 0, 1),
        (0.5, 0, 1),
        (0, 0.5, 1),
        (0, 1, 1),
        (0, 1, 0.5),
        (0.5, 1, 0),
        (0.8536, 1, 0),
        (1, 1, 0),
        (1, 0.9619, 0),
        (1, 0.8536, 0),
        (1, 0.6913, 0),
        (1, 0.5, 0),
        (1, 0.3087, 0),
        (1, 0.1464, 0),
        (1, 0.0381, 0),
        (0.9, 0, 0),
        (0.7, 0, 0),
        (0.4, 0, 0),
        (0.2, 0, 0),
        (1, 0, 1),
        (1, 0, 1),
    ],
    levels=range(-48, 57, 4),
    units="celsius",
)
