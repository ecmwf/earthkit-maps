from earthkit.maps import styles

WIND = styles.Barbs(
    regrid_shape = 40,
    width = 0.001,
    length = 4,
    barbcolor = 'grey',
    sizes = {'emptybarb': 0}
)
