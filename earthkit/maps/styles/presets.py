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
    levels=range(-40, 41, 5),
    units="celsius",
)

MEAN_SEA_LEVEL_PRESSURE_IN_HPA = styles.Contour(
    line_colors="#33334d",
    linewidths=[0.5, 0.5, 0.5, 1],
    labels=True,
    level_step=4,
    units="hPa",
    legend_type=None,
)


WIND_GUST_AT_10M_OVER_6_HOURS_IN_METRES_PER_SECOND = styles.Contour(
    colors=["#73A3FF", "#0080FF", "#6CA632", "#FF8000", "#FF0A00", "#7B12B3"],
    line_colors="navy",
    levels=range(10, 45, 5),
    extend="max",
)


EFI_WIND_GUST_AT_10M = styles.Hatched(
    levels=[0.6, 0.8, 1.0],
    hatches=["." * 5, "o" * 5],
    legend_type="disjoint",
    colors="magenta",
)


EFI_TOTAL_PRECIPITATION = styles.Hatched(
    levels=[0.6, 0.8, 1.0],
    hatches=["." * 5, "o" * 5],
    colors="green",
)
