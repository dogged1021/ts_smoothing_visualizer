"""Localized, theme-aware Plotly presentation; no Streamlit state."""

from functools import partial

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from numpy.typing import NDArray
from plotly.subplots import make_subplots

from tslab.i18n import translate

METHOD_COLORS = {
    "MA（居中）": "#1f77b4",
    "MA（后向）": "#8c564b",
    "EMA": "#ff7f0e",
    "SavGol": "#2ca02c",
    "LOWESS": "#d62728",
    "Gaussian": "#9467bd",
    "Kalman": "#17becf",
}

DARK_METHOD_COLORS = {
    "MA（居中）": "#7AB8F0",
    "MA（后向）": "#D4A48C",
    "EMA": "#FFB56B",
    "SavGol": "#79D38B",
    "LOWESS": "#FF8585",
    "Gaussian": "#BCA3E8",
    "Kalman": "#64D4DF",
}

DERIVATIVE_COLORS = {
    "直接差分": ("#1f77b4", "#7AB8F0"),
    "EMA 后差分": (METHOD_COLORS["EMA"], DARK_METHOD_COLORS["EMA"]),
    "Gaussian 后差分": (METHOD_COLORS["Gaussian"], DARK_METHOD_COLORS["Gaussian"]),
    "SavGol 直接求导": (METHOD_COLORS["SavGol"], DARK_METHOD_COLORS["SavGol"]),
}


def _theme_layout(theme: str) -> dict:
    return {
        "template": "plotly_dark" if theme == "dark" else "plotly_white",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#E7EDF5" if theme == "dark" else "#262730"},
    }


def signal_figure(
    time: pd.Index,
    observed: NDArray[np.float64],
    estimates: dict[str, NDArray[np.float64]],
    truth: NDArray[np.float64] | None = None,
    opacity: float = 0.3,
    *,
    language: str = "zh",
    theme: str = "light",
) -> go.Figure:
    """Compare observations, optional truth and estimates on one time axis."""
    t = partial(translate, language=language)
    colors = DARK_METHOD_COLORS if theme == "dark" else METHOD_COLORS
    figure = go.Figure(layout=_theme_layout(theme))
    figure.add_trace(go.Scatter(
        x=time, y=observed, name=t("原始观测"),
        line={"color": "#B8C2CF" if theme == "dark" else "#707070", "width": 1}, opacity=opacity
    ))
    if truth is not None:
        figure.add_trace(go.Scatter(
            x=time, y=truth, name=t("干净真值"),
            line={"color": "#F0F3F8" if theme == "dark" else "#222222", "width": 2, "dash": "dash"}
        ))
    for name, values in estimates.items():
        figure.add_trace(go.Scatter(
            x=time, y=values, name=t(name), line={"color": colors[name], "width": 2}, connectgaps=False
        ))
    figure.update_layout(
        height=480,
        margin={"l": 20, "r": 20, "t": 45, "b": 20},
        xaxis_title=t("时间" if isinstance(time, pd.DatetimeIndex) else "时间（s）"),
        yaxis_title=t("信号值"),
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.12},
    )
    return figure


def error_figure(
    time: pd.Index, estimates: dict[str, NDArray[np.float64]], truth: NDArray[np.float64],
    *, language: str = "zh", theme: str = "light",
) -> go.Figure:
    """Show signed estimation errors using the same method colors."""
    t = partial(translate, language=language)
    colors = DARK_METHOD_COLORS if theme == "dark" else METHOD_COLORS
    figure = go.Figure(layout=_theme_layout(theme))
    for name, values in estimates.items():
        figure.add_trace(go.Scatter(
            x=time, y=values - truth, name=t(name), line={"color": colors[name]}, connectgaps=False
        ))
    figure.add_hline(y=0, line_width=1, line_color="#999999")
    figure.update_layout(
        height=280, margin={"l": 20, "r": 20, "t": 35, "b": 20}, hovermode="x unified",
        xaxis_title=t("时间" if isinstance(time, pd.DatetimeIndex) else "时间（s）"),
        yaxis_title=t("估计 − 真值"), legend={"orientation": "h"},
    )
    return figure


def derivative_figure(
    time: pd.Index,
    observed: NDArray[np.float64],
    truth: dict[str, NDArray[np.float64]],
    estimates: dict[str, dict[str, NDArray[np.float64]]],
    boundary: tuple[int, int] = (0, 0),
    *, language: str = "zh", theme: str = "light",
) -> go.Figure:
    """Show signal, d1 and d2 with linked time axes and grouped method legends."""
    t = partial(translate, language=language)
    figure = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06)
    figure.update_layout(**_theme_layout(theme))
    figure.add_trace(go.Scatter(
        x=time, y=observed, name=t("原始观测"), opacity=0.8,
        mode="lines+markers", marker={"size": 4}, zorder=1,
        line={"color": "#B8C2CF" if theme == "dark" else "#707070", "width": 1},
    ), row=1, col=1)
    labels = ("信号 s(t)（u）", "一阶导数（u/s）", "二阶导数（u/s²）")
    for row, (key, label) in enumerate(zip(("signal", "d1", "d2"), labels), start=1):
        figure.add_trace(go.Scatter(
            x=time, y=truth[key], name=t("干净真值"), legendgroup="truth", showlegend=row == 1,
            line={"color": "#F0F3F8" if theme == "dark" else "#222222", "width": 2, "dash": "dash"},
        ), row=row, col=1)
        for name, result in estimates.items():
            figure.add_trace(go.Scatter(
                x=time, y=result[key], name=t(name), legendgroup=name, showlegend=row == 1,
                line={"color": DERIVATIVE_COLORS[name][int(theme == "dark")], "width": 1.5},
                connectgaps=False,
            ), row=row, col=1)
        figure.update_yaxes(title_text=t(label), row=row, col=1)
    left, right = boundary
    if left + right >= len(time):
        regions = [(time[0], time[-1])]
    else:
        regions = []
        if left:
            regions.append((time[0], time[left]))
        if right:
            regions.append((time[-right - 1], time[-1]))
    for start, end in regions:
        figure.add_vrect(
            x0=start, x1=end, fillcolor="rgba(128,128,128,0.12)", line_width=0,
            layer="below", row="all", col=1,
        )
    figure.update_xaxes(title_text=t("时间（s）"), row=3, col=1)
    figure.update_layout(
        height=820, margin={"l": 20, "r": 20, "t": 55, "b": 20}, hovermode="x unified",
        legend={"orientation": "h", "y": 1.06, "groupclick": "togglegroup"},
    )
    return figure
