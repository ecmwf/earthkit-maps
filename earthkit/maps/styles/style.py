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


from earthkit.maps import schema


class Style:
    """
    Class describing a mapping style.

    Parameters
    ----------
    colors : str or list or matplotlib.colors.Colormap, optional
        The colors to be used in this `Style`. This can be a
        `named matplotlib colormap <https://matplotlib.org/stable/gallery/color/colormap_reference.html>`__,
        a list of colors (as named CSS4 colors, hexadecimal colors or three
        (four)-element lists of RGB(A) values), or a pre-defined matplotlib
        colormap object. If not provided, the default colormap of the active
        `schema` will be used.
    levels : list or dict, optional
        The levels to use in this `Style`. This can be a list of specific
        levels, or a dictionary containing a `step` and an
        If not provided, some suitable levels
        will be generated automatically (experimental!).
    units : str, optional
        The units in which the levels are defined. If this `Style` is used with
        data not using the given units, then a conversion will be attempted;
        any data incompatible with these units will not be able to use this
        `Style`. If `units` are not provided, then data plotted using this
        `Style` will remain in their original units.

    """

    def __init__(
        self,
        colors=schema.cmap,
        levels=None,
        units=None,
        divergence_point=None,
        level_step=None,
        level_multiple=None,
        units_override=None,
        normalize=True,
        legend_type="colorbar",
        categories=None,
        conversion=None,
        ticks=None,
        gradients=None,
        missing=None,
        **kwargs,
    ):
        self._colors = colors

        self._levels = levels
        self._level_step = level_step
        self._level_multiple = level_multiple
        self._divergence_point = divergence_point

        self.legend_type = legend_type
        self._legend_kwargs = kwargs.get("legend_kwargs", {})
        if ticks is not None:
            self._legend_kwargs["ticks"] = ticks
        self.gradients = gradients

        self._units = units
        self._units_override = units_override
        self.normalize = normalize
        self.kwargs = kwargs

        self.conversion = conversion

        self._categories = categories

        self._missing = missing
