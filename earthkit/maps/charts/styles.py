import re
import warnings

import matplotlib
import numpy as np
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap

from earthkit.maps.schema import schema

MAPPED_COLORS = {
    "mask": (0, 0, 0, 0),
}


def colormap(cmap, levels):
    n_colors = len(levels) - 1

    if not isinstance(cmap, (list, tuple)):
        colors = [matplotlib.cm.get_cmap(cmap)(i) for i in np.linspace(0, 1, n_colors)]
    else:
        colors = [read_color(color) for color in cmap]
    colormap = LinearSegmentedColormap.from_list(name="", colors=colors, N=n_colors)
    colormap.set_under((0, 0, 0, 0))

    norm = BoundaryNorm(levels, colormap.N)

    return colormap, norm


def read_color(color):
    if isinstance(color, str):
        if color.lower() == "none":
            color = "#ffffff"
        elif color.lower().startswith("rgb"):
            result = re.search("\(([^)]+)", color)  # noqa: W605
            if result is None:
                raise ValueError(f"unrecognised color {color}")
            else:
                color = tuple(float(x) for x in result.group(1).split(","))
    return color


def dynamic(normalize=False):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if "colors" in kwargs:
                style = kwargs.pop("style", None)
                if style is not None:
                    warnings.warn(
                        f"Both 'colors' and 'style' passed to {method.__name__}; "
                        f"using 'colors' instead of 'style'"
                    )
                kwargs["cmap"] = kwargs.pop("colors")
            else:
                kwargs["cmap"] = kwargs.pop("style", kwargs.pop("cmap", schema.default_style))

            if normalize and "levels" in kwargs:
                cmap, norm = colormap(kwargs.pop("cmap"), kwargs["levels"])
                kwargs.update({"cmap": cmap, "norm": norm})

            color_bounds = []
            for kwarg in ("under_vmin", "over_vmax"):
                breach_color = kwargs.pop(kwarg, None)
                if breach_color is not None:
                    direction, threshold_key = kwarg.split("_")
                    threshold_value = kwargs.get(threshold_key)
                    if threshold_value is None:
                        raise ValueError(
                            f"'{kwarg}' can only be passed if '{threshold_key}' "
                            f"is also passed"
                        )
                    breach_color = MAPPED_COLORS.get(breach_color, breach_color)
                    color_bounds.append((f"set_{direction}", breach_color))

            result = method(self, *args, **kwargs)
            layer = self._layers[-1].layer

            for function, arg in color_bounds:
                getattr(layer.cmap, function)(arg)

            return result

        return wrapper

    return decorator