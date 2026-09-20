"""Plotly presentation shared by signal experiments; no Streamlit state."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from numpy.typing import NDArray

METHOD_COLORS = {
    "MA（居中）": "#1f77b4",
    "MA（后向）": "#8c564b",
    "EMA": "#ff7f0e",
    "SavGol": "#2ca02c",
    "LOWESS": "#d62728",
    "Gaussian": "#9467bd",
    "Kalman": "#17becf",
}


def signal_figure(
    time: pd.Index,
    observed: NDArray[np.float64],
    estimates: dict[str, NDArray[np.float64]],
    truth: NDArray[np.float64] | None = None,
    opacity: float = 0.3,
) -> go.Figure:
    """Compare observations, optional truth and estimates on one time axis."""
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=time, y=observed, name="原始观测", line={"color": "#707070", "width": 1}, opacity=opacity
    ))
    if truth is not None:
        figure.add_trace(go.Scatter(
            x=time, y=truth, name="干净真值", line={"color": "#222222", "width": 2, "dash": "dash"}
        ))
    for name, values in estimates.items():
        figure.add_trace(go.Scatter(
            x=time, y=values, name=name, line={"color": METHOD_COLORS[name], "width": 2}, connectgaps=False
        ))
    figure.update_layout(
        height=480,
        margin={"l": 20, "r": 20, "t": 45, "b": 20},
        xaxis_title="时间" if isinstance(time, pd.DatetimeIndex) else "时间（s）",
        yaxis_title="信号值",
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.12},
    )
    return figure


def error_figure(time: pd.Index, estimates: dict[str, NDArray[np.float64]], truth: NDArray[np.float64]) -> go.Figure:
    """Show signed estimation errors using the same method colors."""
    figure = go.Figure()
    for name, values in estimates.items():
        figure.add_trace(go.Scatter(
            x=time, y=values - truth, name=name, line={"color": METHOD_COLORS[name]}, connectgaps=False
        ))
    figure.add_hline(y=0, line_width=1, line_color="#999999")
    figure.update_layout(
        height=280, margin={"l": 20, "r": 20, "t": 35, "b": 20}, hovermode="x unified",
        xaxis_title="时间" if isinstance(time, pd.DatetimeIndex) else "时间（s）",
        yaxis_title="估计 − 真值", legend={"orientation": "h"},
    )
    return figure
