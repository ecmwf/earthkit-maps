import matplotlib.pyplot as plt

from . import titles


def continuous_colorbar(self, args, axis, orientation, kwargs):
    colorbar = plt.colorbar(
        self.layer,
        *args,
        orientation=orientation,
        cax=axis,
        **kwargs,
    )
    colorbar.ax.minorticks_off()
    return colorbar


def discrete(axis):
    pass


def categorical(axis):
    pass


LEGEND_MODES = {
    "continuous": continuous_colorbar,
    "discrete": discrete,
    "categorical": categorical,
}


FALLBACK_LEGEND = continuous_colorbar


def _default_legend(layer_type):
    from cartopy.mpl import contour, geocollection
    return {
        geocollection.GeoQuadMesh: continuous_colorbar,
        contour.GeoContourSet: continuous_colorbar,
    }.get(layer_type, FALLBACK_LEGEND)


def legend(
    data_layer,
    *args,
    chart,
    mode=None,
    orientation=None,
    location=None,
    title=None,
    **kwargs,
):
    if data_layer._legend is False:
        return

    if orientation and location:
        raise ValueError(
            "'orientation' and 'location' are mutually exclusive arguments"
        )
    elif orientation is not None:
        location = "right" if orientation == "vertical" else "bottom"
    elif location is None:
        # Default to a colorbar on the right if the plot is portrait, or the
        # bottom if it's landscape
        location = "right" if chart.is_portrait() else "bottom"
    data_layer._legend_location = location
    orientation = "vertical" if location in ("left", "right") else "horizontal"

    # Create an arbitrary axis; this will be moved by mpl tight_layout
    data_layer._legend_ax = chart.fig.add_axes([0, 0, 0.1, 0.1])
    chart.fig.canvas.mpl_connect("resize_event", chart._resize_colorbars)

    if mode is None:
        draw_legend = _default_legend(type(data_layer.layer))
    else:
        if mode in LEGEND_MODES:
            draw_legend = LEGEND_MODES[mode]
        else:
            raise ValueError(
                f"invalid mode {mode}; must be one of "
                f"{','.join(list(LEGEND_MODES))}"
            )

    data_layer._legend = draw_legend(data_layer, args, data_layer._legend_ax, orientation, kwargs)
    if location == "left":
        data_layer._legend_ax.yaxis.set_ticks_position("left")

    rotation = {"right": 270, "left": 90, "top": 0, "bottom": 0}[location]
    labelpad = {"right": 20, "left": -60, "top": -60, "bottom": 0}[location]
    data_layer._legend.set_label(
        titles.colorbar_title(title, data_layer),
        rotation=rotation,
        labelpad=labelpad,
    )

    ticks = {
        "vertical": data_layer._legend.ax.get_yticklabels(),
        "horizontal": data_layer._legend.ax.get_xticklabels(),
    }[orientation]

    chart._resize_colorbars()
