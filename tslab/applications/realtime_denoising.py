"""A01 manual arrival simulation, with explicit publication and target times."""

from functools import partial

import numpy as np
import pandas as pd
import streamlit as st

from tslab.i18n import translate
from tslab.metrics import comparison_metrics
from tslab.plotting import signal_figure
from tslab.realtime import CAUSAL_METHODS, DELAYED_METHODS, replay_signal
from tslab.timing import smoothing_timing
from tslab.ui import odd_window, replay_controls, lowpass_controls


def render(frame: pd.DataFrame, dt: float, language: str, theme: str) -> None:
    """Replay the arrived prefix from scratch; future values never enter the estimator."""
    t = partial(translate, language=language)
    st.caption(t("逐帧回放已有数据，不接入实时设备。只计算已到达观测；曲线按被估计时刻对齐。"))
    left, right = st.columns(2)
    selected = left.multiselect(
        t("无需等待未来帧"), CAUSAL_METHODS, default=["SG-endpoint", "Gaussian（单边）"], format_func=t, key="rt_causal",
    ) + right.multiselect(
        t("需要固定等待"), DELAYED_METHODS, default=list(DELAYED_METHODS), format_func=t, key="rt_delayed",
    )
    settings = {}
    window, degree = 5, 2
    if any(name in selected for name in ("MA（后向）", "SG-endpoint", "SG（固定延迟）", "Gaussian（单边）", "Gaussian（固定延迟）")):
        with st.expander(t("窗口方法 · 参数")):
            if "rt_window" not in st.session_state:
                st.session_state.rt_window = min(5, len(frame) if len(frame) % 2 else len(frame) - 1)
            window = odd_window(t("窗口（样本）"), len(frame), "rt_window")
            if any(name.startswith("SG") for name in selected):
                maximum = min(5, window - 1)
                if st.session_state.get("rt_degree", 2) > maximum:
                    st.session_state.rt_degree = maximum
                degree = st.select_slider(
                    t("多项式阶数"), list(range(1, maximum + 1)), value=2, key="rt_degree",
                )
            if any(name.startswith("Gaussian") for name in selected):
                settings["sigma"] = st.slider(t("σ（样本）"), 0.1, 10.0, 1.0, 0.1, key="rt_sigma")
                st.caption(t("Gaussian 与 SG 共用窗口点数；两种 Gaussian 共用 σ。单边核在当前点权重最大，中心核对称；相同窗口不代表相同平滑强度。"))
            st.caption(t("窗口方法共用窗口长度；两种 SG 共用阶数，仅求值位置不同。完整窗口形成前不输出。"))
    if "EMA" in selected:
        with st.expander(t("{name} · 参数", name="EMA")):
            settings["alpha"] = st.slider(t("平滑因子 α"), 0.01, 1.0, 0.1, 0.01, key="rt_alpha")
            st.caption(t("使用固定系数递推。"))
    if "Kalman" in selected:
        with st.expander(t("{name} · 参数", name="Kalman")):
            settings["process_variance"] = st.number_input(
                t("过程方差 Q"), 0.0, 10.0, 0.05, 0.01, key="rt_q",
            )
            settings["observation_variance"] = st.number_input(
                t("观测方差 R"), 0.001, 10.0, 0.2, 0.01, key="rt_r",
            )
    if "Butterworth（单向）" in selected:
        cutoff, order = lowpass_controls(dt, "rt_lp", language)
        settings.update(dt=dt, cutoff=cutoff, order=order)
    settings.update(window=window, degree=degree)
    count = replay_controls(frame, selected, settings, "rt", language)
    prefix = frame.iloc[:count]
    values = prefix["value"].to_numpy(dtype=float)
    truth = prefix["truth"].to_numpy(dtype=float) if "truth" in prefix else None
    estimates, rows = {}, []
    for name in selected:
        result, delay, startup = replay_signal(values, name, **settings)
        estimates[name] = result
        valid = np.flatnonzero(np.isfinite(result))
        timing_settings = {key: value for key, value in settings.items() if key != "dt"}
        timing = smoothing_timing(name, dt, **timing_settings)
        timing.pop("未来等待（帧）")
        timing["理论值适用范围"] = t(timing["理论值适用范围"])
        rows.append({
            **{t(key): value for key, value in timing.items()},
            t("方法"): t(name), t("等待帧数"): delay, t("等待时间（秒）"): delay * dt,
            t("启动所需帧数"): startup,
            t("最新估计对应时刻"): str(prefix.index[valid[-1]]) if len(valid) else t("尚未输出"),
        })
    st.caption(t("已到达 {count}/{total} 帧 · 当前时刻：{time}", count=count, total=len(frame), time=str(prefix.index[-1])))
    figure = signal_figure(prefix.index, values, estimates, truth, 0.8, language=language, theme=theme)
    for trace in figure.data:
        trace.mode = "lines+markers"
        trace.marker.size = 4
    figure.add_shape(type="line", x0=prefix.index[-1], x1=prefix.index[-1], y0=0, y1=1,
                     xref="x", yref="paper", line={"color": "#999999", "dash": "dot"})
    figure.update_xaxes(range=[frame.index[0], frame.index[-1]])
    st.plotly_chart(figure, width="stretch", theme=None)
    st.caption(t("竖线为当前到达时刻。等待帧数不含启动过程，也不等于响应滞后；末尾未发布估计保持空缺。"))
    if not estimates:
        st.info(t("请选择至少一种算法进行比较。当前显示原始观测及可用真值。"))
        return
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption(t("低频等效滞后是相对目标时间的群延迟极限，非计算耗时或未来等待；空值表示无统一有限值。"))
    st.subheader(t("任务指标"))
    table = comparison_metrics(values, estimates, truth)
    st.dataframe(table.rename(index=t, columns=t).rename_axis(t("方法")), width="stretch")
    st.caption(t("误差和 RPR 仅在已发布结果的共同目标时刻上计算；无共同有效点时留空，不代表零误差。"))
    if not table["有效点数"].iloc[0]:
        st.info(t("等待更多数据形成共同有效点。"))
