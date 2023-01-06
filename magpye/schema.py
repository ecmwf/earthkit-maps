import os

import yaml

from magpye import definitions
from magpye.domains import parse_crs
from magpye.utils import recursive_dict_update

DEFAULT_SCHEMA = "default"


class SchemaNotFoundError(FileNotFoundError):
    pass


class _set:
    def __init__(self, schema, **kwargs):
        self.schema = schema

        keys = [key for key in kwargs if key in self.schema]

        self.old_kwargs = {key: self.schema.get(key) for key in keys}
        self.old_kwargs = {
            **self.old_kwargs,
            **{
                key: dict(value)
                for key, value in self.old_kwargs.items()
                if isinstance(value, Schema)
            },
        }

        self.new_kwargs = [key for key in kwargs if key not in self.schema]
        self.schema.update(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.schema.update(**self.old_kwargs)
        for key in self.new_kwargs:
            self.schema.pop(key, None)


class Schema(dict):

    parsers = {
        "reference_crs": parse_crs,
    }

    def __init__(self, **kwargs):
        self.update(**kwargs)

    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(key)

    def __setattr__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, Schema):
            value = Schema(**value)
        try:
            self[key] = value
        except KeyError:
            raise AttributeError(key)

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.parsers:
                value = self.parsers[key](value)
            setattr(self, key, value)

    def apply(self):
        def decorator(function):
            def wrapper(*args, **kwargs):
                return function(*args, **self._update_kwargs(kwargs))

            return wrapper

        return decorator

    def _update_kwargs(self, kwargs):
        return recursive_dict_update(self.to_dict(), kwargs)

    def to_dict(self):
        d = dict()
        for key in self:
            value = getattr(self, key)
            if isinstance(value, type(self)):
                value = value.to_dict()
            d[key] = value
        return d

    def set(self, **kwargs):
        return _set(self, **kwargs)

    def get(self, key):
        return getattr(self, key)

    def use(self, name):
        file_name = definitions.SCHEMA_DIR / f"{name}.yaml"
        if not os.path.exists(file_name):
            raise SchemaNotFoundError(f"no schema '{name}' found")
        with open(file_name, "r") as f:
            kwargs = yaml.load(f, Loader=yaml.SafeLoader)
        self.reset(**kwargs)

    def reset(self, **kwargs):
        self.__init__(**kwargs)


schema = Schema()
schema.use(DEFAULT_SCHEMA)
