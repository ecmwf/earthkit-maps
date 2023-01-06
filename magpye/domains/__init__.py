import cartopy.crs as ccrs

DEFAULT_CRS = ccrs.PlateCarree()


def parse_crs(crs):
    if crs is None:
        crs = DEFAULT_CRS

    if not isinstance(crs, ccrs.CRS):
        if isinstance(crs, dict):
            crs = crs_from_dict(crs)
        else:
            crs = crs_from_string(crs)

    return crs


def crs_from_dict(kwargs):
    crs = crs_from_string(kwargs.pop("name")).__class__
    return crs(**kwargs)


def crs_from_string(string):
    try:
        crs = getattr(ccrs, string)()
    except AttributeError:
        raise ValueError(f"cartopy has no CRS named '{string}'")
    return crs
