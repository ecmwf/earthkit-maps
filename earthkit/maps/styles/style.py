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
from earthkit.maps.styles.levels import Levels


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
    levels : list or earthkit.maps.styles.levels.Levels, optional
        The levels to use in this `Style`. This can be a list of specific
        levels, or an earthkit `Levels` object. If not provided, some suitable
        levels will be generated automatically (experimental!).
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
    ):
        self._colors = colors
        self._levels = levels if isinstance(levels, Levels) else Levels(levels)
        self._units = units

    def levels(self, data):
        """
        Generate levels specific to some data.

        Parameters
        ----------
        data : numpy.ndarray or xarray.DataArray or earthkit.data.core.Base
            The data for which to generate a list of levels.

        Returns
        -------
        list
        """
        return self._levels.apply(data)
