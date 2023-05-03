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

import glob
import os

from matplotlib import font_manager, rcParams

from earthkit.maps._definitions import FONTS_DIR
from earthkit.maps.schema import schema


def register_fonts():
    fontpaths = glob.glob(os.path.join(FONTS_DIR, "*"))
    for fontpath in fontpaths:
        font_files = glob.glob(os.path.join(fontpath, "*.ttf"))
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)


register_fonts()
rcParams["font.family"] = schema.font