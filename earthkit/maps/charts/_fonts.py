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