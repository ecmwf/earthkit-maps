import matplotlib.pyplot as plt
import numpy as np

from earthkit.maps.metadata import labels

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

    if "ticks" not in kwargs and len(np.unique(np.ediff1d(layer.layer.levels))):
        kwargs["ticks"] = layer.layer.levels

    cbar = plt.colorbar(layer.layer, orientation=orientation, **kwargs)

    if title:
        rotation = {"right": 270, "left": 90, "top": 0, "bottom": 0}[location]
        labelpad = {"right": 20, "left": -60, "top": -60, "bottom": 0}[location]
        cbar.set_label(
            labels.title_from_layer(layer, title),
            rotation=rotation,
            labelpad=labelpad,
        )

    cbar.auto = auto  # indicate whether the colorbar location is automatic

    cbar.location = location

    return cbar
