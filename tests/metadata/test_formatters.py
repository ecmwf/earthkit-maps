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

from datetime import datetime

from earthkit.maps.metadata import formatters


def test_BaseFormatter_conversion():
    assert formatters.BaseFormatter().format("My {test!u}") == "My TEST"
    assert formatters.BaseFormatter().format("My {TeSt!l}") == "My test"


def test_TimeFormatter_time():
    time = datetime(2020, 1, 1)
    assert formatters.TimeFormatter(time).time == [datetime(2020, 1, 1)]


def test_TimeFormatter_base_time():
    time = {
        "base_time": datetime(2020, 1, 1),
        "valid_time": datetime(2020, 1, 7),
    }
    assert formatters.TimeFormatter(time).base_time == [datetime(2020, 1, 1)]


def test_TimeFormatter_valid_time():
    time = {
        "base_time": datetime(2020, 1, 1),
        "valid_time": datetime(2020, 1, 7),
    }
    assert formatters.TimeFormatter(time).valid_time == [datetime(2020, 1, 7)]


def test_TimeFormatter_lead_time():
    time = {
        "base_time": datetime(2020, 1, 1),
        "valid_time": datetime(2020, 1, 7),
    }
    assert formatters.TimeFormatter(time).lead_time == [144]
