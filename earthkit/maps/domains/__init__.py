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

from earthkit.maps.domains import bounds, crs, optimal
from earthkit.maps.domains.domain import Domain

__all__ = [
    "bounds",
    "crs",
    "optimal",
    "Domain",
]


def parse(domain, crs):
    from earthkit.data.utils.bbox import BoundingBox
    from earthkit.data.utils.projections import Projection

    from earthkit.maps.schemas import schema

    if isinstance(domain, BoundingBox):
        domain = [domain.west, domain.east, domain.south, domain.north]

    if isinstance(crs, Projection):
        crs = crs.to_cartopy_crs()

    if isinstance(domain, str):
        domain = Domain.from_string(domain, crs)
    elif domain is not None or crs is not None:
        domain = Domain(domain, crs)
    else:
        domain = Domain(domain, schema.reference_crs)
    return domain
