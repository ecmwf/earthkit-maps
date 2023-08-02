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

import matplotlib.pyplot as plt
import numpy as np

# from earthkit.maps.metadata import labels

DEFAULT_COLORBAR_TITLE = "{variable_name} ({units})"


def colorbar(
    layer,
    title=DEFAULT_COLORBAR_TITLE,
    orientation=None,
    location=None,
    format="g",
    **kwargs,
):
    if orientation and location:
        raise ValueError(
            "'orientation' and 'location' are mutually exclusive arguments"
        )
    elif orientation is not None:
        location = "right" if orientation == "vertical" else "bottom"
    elif location is None:
        # Default to a colorbar on the right
        location = "right"
    orientation = "vertical" if location in ("left", "right") else "horizontal"

    auto = False
    if not any(key in kwargs for key in ("cax", "x", "y")):
        kwargs["cax"] = layer._chart.fig.add_axes([0, 0, 0, 0])
        auto = True

    if format is not None:
        kwargs["format"] = lambda x, _: f"{x:{format}}"

    try:
        levels = layer.layer.norm.boundaries
    except AttributeError:
        levels = layer.layer.levels
    if "ticks" not in kwargs and len(np.unique(np.ediff1d(levels))) != 1:
        kwargs["ticks"] = levels

    cbar = plt.colorbar(layer.layer, orientation=orientation, **kwargs)

    # if title:
    #     rotation = {"right": 270, "left": 90, "top": 0, "bottom": 0}[location]
    #     labelpad = {"right": 20, "left": -60, "top": -60, "bottom": 0}[location]
    #     cbar.set_label(
    #         labels.title_from_layer(layer, title),
    #         rotation=rotation,
    #         labelpad=labelpad,
    #     )

    cbar.auto = auto  # indicate whether the colorbar location is automatic

    cbar.location = location

    return cbar
