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

from earthkit.maps.styles import levels


def test_auto_range():
    # diverging at zero
    assert levels.auto_range(
        [-1, 4],
        divergence_point=0,
        n_levels=5,
    ) == [-4, -2, 0, 2, 4]


def test_step_range():
    assert levels.step_range([3], step=4) == [0, 4]
    assert levels.step_range([2], step=4, reference=3) == [-1, 3]

    assert levels.step_range([3.2], step=0.5) == [3, 3.5]

    assert levels.step_range([1, 3, 7], step=4) == [0, 4, 8]
    assert levels.step_range([1, 3, 7], step=4, reference=2) == [-2, 2, 6, 10]

    assert levels.step_range(
        [983, 1023],
        step=4,
        reference=1000,
    ) == [980, 984, 988, 992, 996, 1000, 1004, 1008, 1012, 1016, 1020, 1024]

    assert levels.step_range(
        [983, 1023],
        step=4,
        reference=1001,
    ) == [981, 985, 989, 993, 997, 1001, 1005, 1009, 1013, 1017, 1021, 1025]


def test_Levels():
    # diverging at zero
    assert levels.Levels(divergence_point=0).apply(
        [-5, 8],
    ) == [-8, -6, -4, -2, 0, 2, 4, 6, 8]

    assert levels.Levels(step=4).apply([3]) == [0, 4]
    assert levels.Levels(step=4, reference=3).apply([2]) == [-1, 3]

    assert levels.Levels(step=4, reference=1000).apply(
        [983, 1023],
    ) == [980, 984, 988, 992, 996, 1000, 1004, 1008, 1012, 1016, 1020, 1024]
