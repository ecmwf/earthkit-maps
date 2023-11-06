from earthkit.maps import styles

TCWV_IN_KG_M2 = styles.Contour(
    colors="viridis",
    extend="both",
    levels=range(0, 150, 10),
    units="kg m-2",
)
