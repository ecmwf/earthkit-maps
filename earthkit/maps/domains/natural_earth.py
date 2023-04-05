
import cartopy.io.shapereader as shpreader

from earthkit.maps import domains


class NaturalEarthDomain:
    """Class for building map domains and CRS based on a Natural Earth shape."""
    
    NATURAL_EARTH_SOURCES = {
        "admin_0_map_units": "NAME_LONG",
        "admin_0_countries": "NAME_LONG",
        "admin_1_states_provinces": "name_en",
    }
    
    def __init__(self, domain_name, crs=None):
        self._domain_name = domain_name
        self._record = None
        self._source = None
        self._crs = None

    @property
    def domain_name(self):
        return self.record.attributes.get(
            self.NATURAL_EARTH_SOURCES[self._source]
        )

    @property
    def record(self):
        if self._record is None:
            for source, attribute in self.NATURAL_EARTH_SOURCES.items():
                shpfilename = shpreader.natural_earth(
                    resolution="110m", category="cultural", name=source
                )
                reader = shpreader.Reader(shpfilename)
                for record in reader.records():
                    name = record.attributes.get(attribute) or ""
                    name = name.replace("\x00", "")
                    if name.lower() == self._domain_name.lower():
                        break
                else:
                    continue
                break
            else:
                raise ValueError(
                    f"No country or state named '{self._domain_name}' found in "
                    f"Natural Earth's shapefiles"
                )
            self._record = record
            self._source = source
        
        return self._record

    @property
    def geometry(self):
        return self.record.geometry

    @property
    def crs(self):
        if self._crs is None:
            bounds = domains.bounds.from_geometry(self.geometry)
            self._crs = domains.optimal.crs_from_bounds(bounds)

        return self._crs

    @property
    def bounds(self, pad=0.1):
        crs_bounds = domains.bounds.from_geometry(self.geometry, crs=self.crs)

        if pad:
            x_offset = (crs_bounds[1] - crs_bounds[0])*pad
            y_offset = (crs_bounds[3] - crs_bounds[2])*pad
            offset = min(x_offset, y_offset)
            crs_bounds = [
                crs_bounds[0] - offset,
                crs_bounds[1] + offset,
                crs_bounds[2] - offset,
                crs_bounds[3] + offset,
            ]

        return crs_bounds
