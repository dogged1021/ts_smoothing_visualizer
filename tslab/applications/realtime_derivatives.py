"""A07 manual replay with per-order publication times and errors."""

from functools import partial

import numpy as np
import pandas as pd
import streamlit as st

from tslab.i18n import translate
from tslab.metrics import derivative_metrics
from tslab.plotting import derivative_figure
from tslab.realtime import replay_derivatives
from tslab.ui import odd_window, replay_controls


def render(frame: pd.DataFrame, dt: float, language: str, theme: str) -> None:
    """Compare zero-wait and fixed-delay estimates using arrived observations only."""
    t = partial(translate, language=language)
    st.caption(t("逐帧回放已有数据，不接入实时设备。只计算已到达观测；曲线按被估计时刻对齐。"))
    left, right = st.columns(2)
    selected = left.multiselect(
        t("无需等待未来帧"), ["后向差分", "EMA 后向差分", "SG-endpoint"],
        default=["SG-endpoint"], format_func=t, key="dr_causal",
    ) + right.multiselect(
        t("需要固定等待"), ["SG（固定延迟）"], default=["SG（固定延迟）"], format_func=t, key="dr_delayed",
    )
    settings = {"dt": dt, "window": 5, "degree": 2, "alpha": 0.1}
    if any(name.startswith("SG") for name in selected):
        with st.expander(t("窗口方法 · 参数")):
            if "dr_window" not in st.session_state:
                st.session_state.dr_window = min(5, len(frame) if len(frame) % 2 else len(frame) - 1)
            window = odd_window(t("窗口（样本）"), len(frame), "dr_window")
            degrees = list(range(2, min(5, window - 1) + 1))
            if st.session_state.get("dr_degree", 2) not in degrees:
                st.session_state.dr_degree = degrees[-1]
            settings["window"] = window
            settings["degree"] = st.select_slider(t("多项式阶数"), degrees, value=2, key="dr_degree")
            st.caption(t("窗口方法共用窗口长度；两种 SG 共用阶数，仅求值位置不同。完整窗口形成前不输出。"))
    if "EMA 后向差分" in selected:
        with st.expander(t("{name} · 参数", name=t("EMA 后向差分"))):
            settings["alpha"] = st.slider(t("平滑因子 α"), 0.01, 1.0, 0.1, 0.01, key="dr_alpha")
    st.caption(t("后向差分与 EMA 后向差分从第 1 帧输出信号，从第 3 帧输出导数；SG 各阶均等待完整窗口。"))
    count = replay_controls(frame, selected, settings, "dr", language)
    prefix = frame.iloc[:count]
    values = prefix["value"].to_numpy(dtype=float)
    truth = {"signal": prefix["truth"].to_numpy(), "d1": prefix["d1"].to_numpy(), "d2": prefix["d2"].to_numpy()}
    estimates, rows = {}, []
    for name in selected:
        result, delay, startups = replay_derivatives(values, name, **settings)
        estimates[name] = result
        for key, label in (("signal", "信号"), ("d1", "一阶导数"), ("d2", "二阶导数")):
            valid = np.flatnonzero(np.isfinite(result[key]))
            rows.append({
                t("方法"): t(name), t("输出"): t(label), t("等待帧数"): delay,
                t("等待时间（秒）"): delay * dt, t("启动所需帧数"): startups[key],
                t("最新估计对应时刻"): str(prefix.index[valid[-1]]) if len(valid) else t("尚未输出"),
            })
    st.caption(t("已到达 {count}/{total} 帧 · 当前时刻：{time}", count=count, total=len(frame), time=str(prefix.index[-1])))
    figure = derivative_figure(prefix.index, values, truth, estimates, language=language, theme=theme)
    for trace in figure.data:
        trace.mode = "lines+markers"
        trace.marker.size = 4
    for row in range(1, 4):
        figure.add_vline(x=float(prefix.index[-1]), line_dash="dot", line_color="#999999", row=row, col=1)
    figure.update_xaxes(range=[frame.index[0], frame.index[-1]])
    st.plotly_chart(figure, width="stretch", theme=None)
    st.caption(t("竖线为当前到达时刻。等待帧数不含启动过程，也不等于响应滞后；末尾未发布估计保持空缺。"))
    if not estimates:
        st.info(t("请选择至少一种算法进行比较。当前显示原始观测及可用真值。"))
        return
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.subheader(t("逐阶误差"))
    table = derivative_metrics(truth, estimates)
    display = table.copy()
    for column in ("输出", "方法"):
        display[column] = display[column].map(t)
    st.dataframe(display.rename(columns=t), hide_index=True, width="stretch")
    st.caption(t("每一阶在相同的共同有效点上比较；不同阶量纲不同，不合并打分。EMA 初始化影响仍计入。"))
    if (table["有效点数"] == 0).any():
        st.info(t("等待更多数据形成共同有效点。"))
