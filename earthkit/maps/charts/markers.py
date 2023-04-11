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


class CustomMarker:
    pass


class oktas(CustomMarker):

    DEFAULT_KWARGS = {
        "color": "white",
        "markeredgecolor": "#333333",
        "markeredgewidth": 0.75,
        "markersize": 10,
    }

    def __init__(self, oktas, **kwargs):
        self.oktas = oktas
        super().__init__(**kwargs)

    def plot(self, chart, *args, **kwargs):
        kwargs = {**self.DEFAULT_KWARGS, **kwargs}
        return {
            0: _zero_oktas,
            1: _one_oktas,
            2: _two_oktas,
            3: _three_oktas,
            4: _four_oktas,
            5: _five_oktas,
            6: _six_oktas,
            7: _seven_oktas,
            8: _eight_oktas,
            9: _nine_oktas,
        }[self.oktas](chart, *args, **kwargs)


def _zero_oktas(chart, *args, **kwargs):
    return (chart.ax.plot(*args, marker="o", **kwargs),)


def _one_oktas(chart, *args, **kwargs):
    return (
        chart.ax.plot(
            *args,
            marker="o",
            markerfacecoloralt=kwargs["color"],
            fillstyle="left",
            **kwargs,
        ),
    )


def _two_oktas(chart, *args, **kwargs):
    layer_0 = chart.ax.plot(
        *args,
        marker="o",
        markerfacecoloralt=kwargs["markeredgecolor"],
        fillstyle="left",
        **{**kwargs, **{"markeredgecolor": "none"}},
    )
    layer_1 = chart.ax.plot(
        *args,
        marker="o",
        markerfacecoloralt="none",
        fillstyle="bottom",
        **{**kwargs, **{"markeredgecolor": "none"}},
    )
    layer_2 = chart.ax.plot(
        *args,
        marker="o",
        **{**kwargs, **{"color": "none"}},
    )
    return (
        layer_0,
        layer_1,
        layer_2,
    )


def _three_oktas(chart, *args, **kwargs):
    layer_0 = chart.ax.plot(
        *args,
        marker="o",
        markerfacecoloralt=kwargs["markeredgecolor"],
        fillstyle="left",
        **{**kwargs, **{"markeredgecolor": "none"}},
    )
    layer_1 = chart.ax.plot(
        *args,
        marker="o",
        markerfacecoloralt="none",
        fillstyle="bottom",
        **{**kwargs, **{"markeredgecolor": "none"}},
    )
    layer_2 = chart.ax.plot(
        *args,
        marker="o",
        markerfacecoloralt="none",
        fillstyle="left",
        **{**kwargs, **{"color": "none"}},
    )
    return (
        layer_0,
        layer_1,
        layer_2,
    )


def _four_oktas(chart, *args, **kwargs):
    return (
        chart.ax.plot(
            *args,
            marker="o",
            markerfacecoloralt=kwargs["markeredgecolor"],
            fillstyle="left",
            **kwargs,
        ),
    )


def _five_oktas(chart, *args, **kwargs):
    layer_0 = _four_oktas(chart, *args, **kwargs)[0]
    layer_1 = chart.ax.plot(
        *args,
        marker="o",
        markerfacecoloralt="none",
        fillstyle="top",
        **{**kwargs, **{"color": "none"}},
    )
    return (
        layer_0,
        layer_1,
    )


def _six_oktas(chart, *args, **kwargs):
    layer_0 = chart.ax.plot(
        *args,
        marker="o",
        markerfacecoloralt=kwargs["markeredgecolor"],
        fillstyle="left",
        **{**kwargs, **{"markeredgecolor": "none"}},
    )
    layer_1 = chart.ax.plot(
        *args,
        marker="o",
        markerfacecoloralt=kwargs["markeredgecolor"],
        fillstyle="top",
        **{**kwargs, **{"color": "none", "markeredgecolor": "none"}},
    )
    layer_2 = chart.ax.plot(*args, marker="o", **{**kwargs, **{"color": "none"}})
    return layer_0, layer_1, layer_2


def _seven_oktas(chart, *args, **kwargs):
    layer_0 = _eight_oktas(chart, *args, **kwargs)[0]
    layer_1 = chart.ax.plot(
        *args,
        marker="|",
        **{
            **kwargs,
            **{
                "markeredgecolor": kwargs["color"],
                "markeredgewidth": kwargs["markeredgewidth"] * 3,
            },
        },
    )
    layer_2 = chart.ax.plot(*args, marker="o", **{**kwargs, **{"color": "none"}})
    return layer_0, layer_1, layer_2


def _eight_oktas(chart, *args, **kwargs):
    return (
        chart.ax.plot(
            *args, marker="o", **{**kwargs, **{"color": kwargs["markeredgecolor"]}}
        ),
    )


def _nine_oktas(chart, *args, **kwargs):
    layer_0 = _zero_oktas(chart, *args, **kwargs)[0]
    layer_1 = chart.ax.plot(
        *args, marker="x", **{**kwargs, **{"markersize": kwargs["markersize"] * 0.71}}
    )
    return layer_0, layer_1
