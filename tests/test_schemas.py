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

from earthkit.maps import schemas


def test_Schema_get():
    schema = schemas.Schema(
        number=1,
        string="hello",
        dictionary={"key": "value"},
    )

    assert schema.number == 1
    assert schema.string == "hello"
    assert schema.dictionary == {"key": "value"}
    assert schema.dictionary.key == "value"


def test_Schema_set():
    schema = schemas.Schema(
        number=1,
    )

    assert schema.number == 1

    schema.number = 2
    assert schema.number == 2

    schema.foo = "bar"
    assert schema.foo == "bar"


def test_Schema_context_manager():
    schema = schemas.Schema(
        number=1,
    )

    assert schema.number == 1

    with schema.set(number=2):
        assert schema.number == 2

    assert schema.number == 1


def test_Schema_recursive_update():
    schema = schemas.Schema(
        dictionary={"foo": "bar", "baz": "qux"},
    )

    assert schema.dictionary.foo == "bar"
    assert schema.dictionary.baz == "qux"

    schema.dictionary.foo = 42
    assert schema.dictionary.foo == 42
    assert schema.dictionary.baz == "qux"


def test_Schema_use():
    schema = schemas.Schema(
        use_preferred_styles=False,
    )

    assert schema.use_preferred_styles is False

    schema.use("ecmwf")

    assert schema.use_preferred_styles is True
