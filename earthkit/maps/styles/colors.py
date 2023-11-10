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

import matplotlib as mpl
import numpy as np
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap


def expand(colors, levels):
    """
    Generate a list of colours from a matplotlib colormap name and some levels.
    """
    if isinstance(colors, (list, tuple)) and len(colors) == 1:
        colors *= len(levels) - 1
    if isinstance(colors, str):
        try:
            cmap = mpl.colormaps[colors]
        except KeyError:
            colors = [colors] * (len(levels) - 1)
        else:
            colors = [cmap(i) for i in np.linspace(0, 1, len(levels))]
    return colors


def gradients(levels, colors, gradients, normalize, **kwargs):

    normalised = (levels - np.min(levels)) / (np.max(levels) - np.min(levels))
    color_bins = list(zip(normalised, colors))
    cmap = LinearSegmentedColormap.from_list(name="", colors=color_bins, N=255)

    if not isinstance(gradients, (list, tuple)):
        gradients = [gradients] * (len(levels) - 1)

    extrapolated_levels = []
    for i in range(len(levels) - 1):
        bins = list(np.linspace(levels[i], levels[i + 1], gradients[i]))
        extrapolated_levels += bins[(1 if i != 0 else 0) :]
    levels = extrapolated_levels

    norm = None
    if normalize:
        norm = BoundaryNorm(levels, cmap.N)

    return {**{"cmap": cmap, "norm": norm, "levels": levels}, **kwargs}
