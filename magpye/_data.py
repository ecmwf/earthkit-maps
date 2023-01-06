from functools import partial

import yaml

from magpye import _definitions

READERS = {
    ".yaml": partial(yaml.load, Loader=yaml.SafeLoader),
}


class DataNotFoundError(FileNotFoundError):
    pass


class AmbiguousDataError(Exception):
    pass


def load(source, data_type=None):
    """
    Load a magpye auxilliary data file.

    Parameters
    ----------
    source : str
        The name of a file (with or without extension) found within magpye/data.
    data_type : str
        If applicable, the name of the subdirectory withing magpye/data in which
        the auxilliary file will be found.
    """
    path = _definitions.DATA_DIR
    if data_type is not None:
        path /= data_type

    matches = list(path.glob(f"{source}*"))
    if not matches:
        raise DataNotFoundError(f"could not find data named '{source}'")
    elif len(matches) > 1:
        raise AmbiguousDataError(
            f"multiple data sources named '{source}'; file extension required"
        )

    path = matches[0]
    reader = READERS.get(path.suffix)
    if reader is None:
        raise KeyError(f"no reader for file with extension {path.suffix}")

    with open(path, "r") as f:
        return reader(f)
