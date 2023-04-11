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
    dict_1 = {"nested": {"a": 1, "b": 2}, "c": 3, "d": 4}
    dict_2 = {"nested": {"a": 10, "c": 3}, "d": 5, "e": 6}

    expected = {"nested": {"a": 10, "b": 2, "c": 3}, "c": 3, "d": 5, "e": 6}

    assert utils.recursive_dict_update(dict_1, dict_2) == expected
