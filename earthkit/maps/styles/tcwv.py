from earthkit.maps import styles

TCWV_IN_KG_M2 = styles.Contour(
    colors="viridis",
    extend="both",
    levels=range(0, 100, 5),
    units="kg m-2",
)
