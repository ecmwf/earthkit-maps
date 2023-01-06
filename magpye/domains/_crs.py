import inspect

import cartopy.crs as ccrs


class CRS:
    def to_ccrs(self, domain):
        return getattr(ccrs, self.cartopy_crs())(**self.get_kwargs(domain))

    def get_kwargs(self, domain):
        attributes = inspect.getmembers(
            self.__class__, lambda attr: not (inspect.isroutine(attr))
        )
        attributes = [
            attr
            for attr in attributes
            if not (attr[0].startswith("__") and attr[0].endswith("__"))
        ]
        return {attr[0].lower(): getattr(domain, attr[1]) for attr in attributes}

    def cartopy_crs(self):
        return self.__class__.__name__


class PlateCarree(CRS):
    CENTRAL_LONGITUDE = "central_lon"


class LambertAzimuthalEqualArea(CRS):
    CENTRAL_LATITUDE = "central_lat"
    CENTRAL_LONGITUDE = "central_lon"


class TransverseMercator(CRS):
    CENTRAL_LATITUDE = "central_lat"
    CENTRAL_LONGITUDE = "central_lon"


class AlbersEqualArea(CRS):
    CENTRAL_LATITUDE = "central_lat"
    CENTRAL_LONGITUDE = "central_lon"
    STANDARD_PARALLELS = "standard_parallels"


class NorthPolarStereo(CRS):
    CENTRAL_LONGITUDE = "central_lon"


class SouthPolarStereo(CRS):
    CENTRAL_LONGITUDE = "central_lon"
