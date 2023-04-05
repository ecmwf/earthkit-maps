
import numpy as np
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader

from magpye import _data, domains
from magpye.schema import schema


DOMAIN_LOOKUP = _data.load("domains")


class Domain:
    
    @classmethod
    def from_string(cls, string, crs=None):
        from . import natural_earth
        domain_name = lookup_name(string)
        
        if domain_name is not None and domain_name in DOMAIN_LOOKUP["domains"]:
            domain_config = DOMAIN_LOOKUP["domains"][domain_name]
            if isinstance(domain_config, list):
                bounds = domain_config
                domain_crs = None
            else:
                bounds = domain_config.get("bounds")
                domain_crs = domain_config.get("crs")
            if crs is not None:
                bounds = domains.bounds.from_bbox(bounds, crs, domains.crs.parse(domain_crs))
            else:
                crs = domains.crs.parse(domain_crs or domains.optimal.crs_from_bounds(bounds))
                if domain_crs is None:
                    crs = domains.optimal.crs_from_bounds(bounds)
                    bounds = domains.bounds.from_bbox(bounds, crs)

        else:
            domain_name = domain_name or string
            source = natural_earth.NaturalEarthDomain(domain_name, crs)
            domain_name = source.domain_name
            bounds = source.bounds
            crs = source.crs

        return cls(bounds, crs, domain_name)
        
    def __init__(self, bounds=None, crs=None, domain_name=None):
        if crs is None:
            self.crs = domains.optimal.crs_from_bounds(bounds)
            self.bounds = domains.bounds.from_bbox(bounds, self.crs)
        else:
            self.crs = domains.crs.parse(crs)
            self.bounds = bounds
        
        self.domain_name = domain_name

    @property
    def title(self):
        if self.domain_name in DOMAIN_LOOKUP["the_countries"]:
            return f"the {self.domain_name}"
        elif self.domain_name is None:
            string = "a custom domain"
            if self.bounds is not None:
                string += f" ({[round(i, 2) for i in self.latlon_bounds]})"
            return string
        return self.domain_name

    @property
    def latlon_bounds(self):
        return domains.bounds.from_bbox(self.bounds, ccrs.PlateCarree(), self.crs)


def lookup_name(domain_name):
    """Format a domain name."""
    # normalise the input string and the lookup key
    domain_name = domain_name.lower().replace("_", " ")
    name_mapping = {k.lower(): k for k in DOMAIN_LOOKUP["domains"]}
    
    if domain_name not in name_mapping:
        for name, alt_names in DOMAIN_LOOKUP["alternate_names"].items():
            if domain_name in [alt_name.lower() for alt_name in alt_names]:
                domain_name = name
                break
        else:
            domain_name = None
    domain_name = name_mapping.get(domain_name, domain_name)        

    return domain_name