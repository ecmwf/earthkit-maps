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

from earthkit.maps import utils


def test_recursive_dict_update():
    original_dict = {"test": {"a": 1, "b": 2}, "foo": "bar", "qux": 42}
    update_dict = {"test": {"b": 3, "c": 4}, "foo": "baz"}

    assert utils.recursive_dict_update(original_dict, update_dict) == {
        "test": {"a": 1, "b": 3, "c": 4},
        "foo": "baz",
        "qux": 42,
    }


def test_list_to_human():
    assert utils.list_to_human(["a"]) == "a"
    assert utils.list_to_human(["a", "b"]) == "a and b"
    assert utils.list_to_human(["a", "b", "c"]) == "a, b and c"
    assert utils.list_to_human(["a", "b", "c"], oxford_comma=True) == "a, b, and c"
    assert utils.list_to_human(["a", "b", "c"], conjunction="et") == "a, b et c"
