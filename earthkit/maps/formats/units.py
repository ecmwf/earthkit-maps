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

from cf_units import Unit
from cf_units.tex import tex

PREFERRED_FORMATS = {
    "celsius": "°C",
    "fahrenheit": "°F",
}


def preferred_format(units):
    for name, symbol in PREFERRED_FORMATS.items():
        if compare_units(units, name):
            break
    else:
        symbol = Unit(units).symbol

    try:
        latex = f"${tex(symbol)}$"
    except (SyntaxError, ValueError):
        try:
            latex = f"${tex(symbol.replace('.', ' '))}$"
        except (SyntaxError, ValueError):
            latex = symbol

    return latex


def compare_units(unit_1, unit_2):
    return Unit(unit_1) == Unit(unit_2)
