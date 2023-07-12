import matplotlib as mpl
import numpy as np
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap

from earthkit.maps import data, schema

EARTHKIT_COLORS = data.load("colors/earthkit.yaml")


def parse_colors(colors):
    parsed_colors = []
    for color in colors:
        parsed_colors.append(EARTHKIT_COLORS.get(color, color))
    return parsed_colors


class Style:
    def __init__(self, levels, colors=None, normalize=True):
        self._colors = colors or schema.cmap
        self._levels = levels
        self._normalize = normalize

    @property
    def colors(self):
        if isinstance(self._colors, str):
            self._colors = [
                mpl.cm.get_cmap(self._colors)(i)
                for i in np.linspace(0, 1, len(self.levels))
            ]
        return self._colors

    @property
    def levels(self):
        return self._levels

    def to_kwargs(self, data):
        cmap = LinearSegmentedColormap.from_list(
            name="", colors=self.colors, N=len(self.colors)
        )

        norm = None
        if self._normalize:
            norm = BoundaryNorm(self.levels, cmap.N)

        return {"cmap": cmap, "norm": norm, "levels": self.levels}


class IntervalStyle(Style):
    def __init__(self, colors=None, step=None):
        super().__init__(colors=colors)
        self._step = step
