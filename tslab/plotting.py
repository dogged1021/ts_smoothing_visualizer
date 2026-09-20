"""Localized, theme-aware Plotly presentation; no Streamlit state."""

from functools import partial

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from numpy.typing import NDArray

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
