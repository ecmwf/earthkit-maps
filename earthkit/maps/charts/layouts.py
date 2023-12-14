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

PRESET_SHAPES = {
    0: (0, 0),
    1: (1, 1),
    2: (1, 2),
    3: (1, 3),
    4: (1, 4),
    5: (2, 3),
    6: (2, 3),
    7: (2, 4),
    8: (2, 4),
    9: (2, 5),
    10: (2, 5),
    11: (3, 4),
    12: (3, 4),
    13: (3, 5),
    14: (3, 5),
    15: (3, 5),
    16: (3, 6),
    17: (3, 6),
    18: (3, 6),
    19: (4, 5),
    20: (4, 5),
}


def rows_cols(num_subplots, rows=None, cols=None, max_cols=8):

    if rows is None and cols is None:
        if num_subplots in PRESET_SHAPES:
            rows, cols = PRESET_SHAPES[num_subplots]
        else:
            cols = max_cols
            rows = num_subplots // max_cols + 1
    elif rows is not None and cols is None:
        if rows == 1:
            cols = num_subplots
        else:
            cols = num_subplots / rows
            if not cols.is_integer():
                cols = int(cols) + 1
            cols = int(cols)
    elif rows is None and cols is not None:
        if cols == 1:
            rows = num_subplots
        else:
            rows = num_subplots / cols
            if not rows.is_integer():
                rows = int(rows) + 1
            rows = int(rows)
    else:
        if rows * cols < num_subplots:
            raise ValueError(
                f"{num_subplots} subplots is too many for a figure with {rows} "
                f"rows and {cols} columns; this figure can contain a maximum "
                f"of {rows*cols} subplots"
            )

    return rows, cols
