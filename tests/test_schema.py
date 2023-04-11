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

from earthkit.maps import schema


def test_default_schema():
    schema.use("default")


def test_use():
    schema.use("light")
    assert schema.colormap == "viridis"


def test_set():
    font = "verdana"
    schema.set(font=font)
    assert schema.font == font


def test_set_nested():
    labels = "foobarbaz"
    schema.contour.set(labels=labels)
    assert schema.contour.labels == labels


def test_set_context_manager():
    font = "verdana"
    schema.set(font=font)

    tmp_font = "comic sans"
    with schema.set(font=tmp_font):
        assert schema.font == tmp_font

    assert schema.font == font
