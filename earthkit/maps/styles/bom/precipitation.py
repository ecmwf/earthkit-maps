# Copyright 2023, Australian Bureau of Meteorology
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

PRECIP_COLOURS =[
        (0.667, 1.0, 1.0),
        (0.333, 0.627, 1.0),
        (0.114, 0.0, 1.0),
        (0.494, 0.898, 0.357),
        (0.306, 0.8, 0.263),
        (0.18, 0.698, 0.224),
        (0.118, 0.6, 0.239),
        (1.0, 1.0, 0.4),
        (1.0, 0.8, 0.4),
        (1.0, 0.533, 0.298),
        (1.0, 0.098, 0.098),
        (0.8, 0.239, 0.239),
        (0.647, 0.192, 0.192),
        (0.918, 0.004, 0.925),
        (0.537, 0.404, 0.902),
        (0.98, 0.941, 0.902)
    ]
PRECIP_LEVELS = [0.1,0.2,0.5,1.0,2.0,5.0,7.5,10,15,20,25,30,35,40,45,50]

PRECIPITATION_IN_MM = styles.Contour(
    labels=True,
    units_override="mm",
    colors = PRECIP_COLOURS,
    levels=PRECIP_LEVELS,
    units="mm",
)

PRECIPITATION_IN_M = styles.Contour(
    labels=True,
    colors=PRECIP_COLOURS,
    levels=list(x / 1000 for x in PRECIP_LEVELS),
    units="m",
)
