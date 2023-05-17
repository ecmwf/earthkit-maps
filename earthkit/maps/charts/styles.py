from cf_units import Unit

from earthkit.maps import _data

EARTHKIT_COLORS = _data.load("colors/earthkit.yaml")

AUTOMATIC_STYLES = _data.load("styles/wind.yaml")


def parse_colors(colors):
    parsed_colors = []
    for color in colors:
        parsed_colors.append(EARTHKIT_COLORS.get(color, color))
    return parsed_colors


def guess(method):
    def wrapper(self, data, *args, **kwargs):
        if not all(kwarg in kwargs for kwarg in ("colors", "levels")):
            kwargs = {**_guess_style(data), **kwargs}
            if "cmap" in kwargs:
                kwargs.pop("colors", None)
        return method(self, data, *args, **kwargs)

    return wrapper


def _guess_style(data, styles=AUTOMATIC_STYLES["styles"]):
    data_units = Unit(_unique_metadata(data, "units"))

    style = dict()
    for style_name, recipe in styles.items():
        if "units" in recipe and Unit(recipe["units"]) != data_units:
            continue
        for match in recipe["metadata-match"]:
            for key in match:
                value = _unique_metadata(data, key)
                if match[key] == value:
                    break
            else:
                break
        else:
            style = recipe["style"]
            break
    return style


def _unique_metadata(data, key):
    value = data.metadata(key)
    if isinstance(value, (list, tuple)):
        value = list(set(value))
        if len(value) != 1:
            raise ValueError(f"data contains multiple {key} values")
        value = value[0]
    return value
