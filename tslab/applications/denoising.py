"""A01: compare noise reduction with explicit data, parameters and evaluation."""

import numpy as np
import pandas as pd
import streamlit as st
from numpy.typing import NDArray

from tslab import algorithms
from tslab.data import DATASETS, SCENARIOS, load_dataset, synthetic_signal, validate_data
from tslab.metrics import comparison_metrics
from tslab.plotting import METHOD_COLORS, error_figure, signal_figure

CAUSAL_METHODS = ["MA（后向）", "EMA", "Kalman"]


def _odd_window(label: str, size: int, key: str) -> int:
    options = list(range(3, min(51, size) + 1, 2))
    if key in st.session_state and st.session_state[key] not in options:
        st.session_state[key] = options[-1]
    default = None if key in st.session_state else min(15, options[-1])
    return st.select_slider(label, options=options, value=default, key=key)


def _data_controls() -> pd.DataFrame:
    left, right = st.columns(2)
    source = left.selectbox("数据来源", ["合成信号（有真值）", "内置数据集"], key="source")
    if source == "合成信号（有真值）":
        scenario = right.selectbox("实验场景", SCENARIOS, key="scenario")
        with st.expander("数据参数", expanded=False):
            left, right = st.columns(2)
            samples = left.number_input("样本数", min_value=3, max_value=2000, value=500, step=1, key="samples")
            dt = right.number_input("采样间隔 Δt（秒）", min_value=0.001, max_value=10.0, value=0.1, format="%.3f", key="dt")
            noise = left.slider("噪声标准差", 0.0, 2.0, 0.3, step=0.05, key="noise")
            seed = right.number_input("随机种子", min_value=0, max_value=1000000, value=42, step=1, key="seed")
        return synthetic_signal(scenario, samples=samples, dt=dt, noise=noise, seed=seed)
    label = right.selectbox("数据集", list(DATASETS), key="dataset")
    frame = load_dataset(DATASETS[label])
    with st.expander("数据参数", expanded=False):
        count = st.number_input(
            "从开头截取的点数（参与计算）", min_value=3, max_value=len(frame),
            value=len(frame), step=1, key=f"points_{DATASETS[label]}",
        )
    st.caption("内置 CSV 未提供干净真值（包括 Noisy Sine），因此仅展示粗糙度等诊断，不计算恢复误差。")
    return frame.iloc[:count].copy()


def _method_controls(name: str, values: NDArray[np.float64], dt: float) -> tuple[NDArray[np.float64], str]:
    """Render one selected method's parameters, then calculate only that method."""
    size = len(values)
    with st.expander(f"{name} · 参数", expanded=False):
        if name in ("MA（居中）", "MA（后向）"):
            center = name == "MA（居中）"
            window = _odd_window("窗口（样本）", size, "ma_center" if center else "ma_trailing")
            note = (
                f"使用未来 {window // 2} 点（{window // 2 * dt:g} 秒）；两端各 {window // 2} 点窗口不完整，保留空缺。"
                if center else f"因果；前 {window - 1} 点为启动空缺，不使用未来回填。"
            )
            result = algorithms.moving_average(values, window, center=center)
        elif name == "EMA":
            alpha = st.slider("平滑因子 α", 0.01, 1.0, 0.1, step=0.01, key="ema_alpha")
            adjust = st.checkbox("起始阶段归一化权重（adjust=True）", value=True, key="ema_adjust")
            st.caption("默认保持原项目行为；取消勾选后采用 y[t] = αx[t] + (1−α)y[t−1]。")
            note = "因果；首值初始化，起始阶段受初始化影响。" + ("使用归一化指数权重。" if adjust else "使用固定系数递推。")
            result = algorithms.exponential_average(values, alpha, adjust=adjust)
        elif name == "SavGol":
            window = _odd_window("窗口（样本）", size, "sg_window")
            degrees = list(range(1, min(5, window - 1) + 1))
            if "sg_degree" in st.session_state and st.session_state["sg_degree"] not in degrees:
                st.session_state["sg_degree"] = degrees[-1]
            default = None if "sg_degree" in st.session_state else min(2, degrees[-1])
            degree = st.select_slider("多项式阶数", options=degrees, value=default, key="sg_degree")
            note = f"非因果；内部点使用未来 {window // 2} 点。两端各 {window // 2} 点由首尾窗口多项式估计（interp）。"
            result = algorithms.savitzky_golay(values, window, degree)
        elif name == "LOWESS":
            minimum = max(0.01, np.ceil(200 / size) / 100)
            current = st.session_state.get("lowess_fraction")
            if current is not None and current < minimum:
                st.session_state["lowess_fraction"] = minimum
            default = None if "lowess_fraction" in st.session_state else max(0.05, minimum)
            fraction = st.number_input(
                "邻域比例 frac", min_value=float(minimum), max_value=1.0,
                value=default, step=0.01, key="lowess_fraction",
            )
            if fraction is None:
                raise ValueError("请输入邻域比例 frac。")
            note = f"非因果；邻域约 {int(fraction * size)} 点，端点使用不对称邻域。保留 3 次稳健重加权，不能视为固定延迟滤波。"
            result = algorithms.local_regression(values, fraction)
        elif name == "Gaussian":
            sigma = st.slider("σ（样本）", 0.1, 10.0, 2.0, step=0.1, key="gaussian_sigma")
            radius = int(4 * sigma + 0.5)
            note = f"非因果；核半径 {radius} 点（{radius * dt:g} 秒），边界使用反射延拓。"
            result = algorithms.gaussian_average(values, sigma)
        elif name == "Kalman":
            left, right = st.columns(2)
            process = left.number_input(
                "过程方差 Q", min_value=0.0, max_value=10.0, value=0.05,
                step=0.01, format="%.3f", key="kalman_q",
            )
            observation = right.number_input(
                "观测方差 R", min_value=0.001, max_value=10.0, value=0.2,
                step=0.01, format="%.3f", key="kalman_r",
            )
            st.caption("输入是方差，不是标准差。Q 是每个采样步的过程方差；更改采样间隔后应重新评估参数。")
            note = "因果；一维随机游走，初始均值取首个观测、初始方差为 1。没有速度或加速度状态。"
            result = algorithms.kalman_filter(values, process, observation)
        else:
            raise ValueError(f"未知算法：{name}")
        st.caption(note)
    return result, note


def render() -> None:
    """Render the first complete application without future application placeholders."""
    st.title("随机降噪与稳定读数")
    st.caption("减少随机抖动，同时观察真实信号的保留程度。A01 · 信号恢复与结构保留")
    try:
        frame = _data_controls()
        dt = validate_data(frame)
    except ValueError as error:
        st.error(str(error))
        return
    st.caption(f"{len(frame)} 个样本 · 采样间隔 {dt:g} 秒 · 等间隔采样")
    mode = st.radio("使用模式", ["离线对比", "仅因果方法"], horizontal=True, key="mode")
    causal = mode == "仅因果方法"
    st.caption("只使用当前与过去的样本；这是历史记录上的因果计算，并非实时设备接入。" if causal else "可同时对比因果与非因果方法；使用未来信息及边界处理方式见下方说明。")
    selected = st.multiselect(
        "对比算法", CAUSAL_METHODS if causal else list(METHOD_COLORS),
        default=["EMA", "Kalman"], key="methods_causal" if causal else "methods_offline",
    )
    values = frame["value"].to_numpy(dtype=float)
    truth = frame["truth"].to_numpy(dtype=float) if "truth" in frame else None
    estimates, notes = {}, {}
    for name in selected:
        try:
            estimates[name], notes[name] = _method_controls(name, values, dt)
        except ValueError as error:
            st.warning(f"{name}：{error}")
    with st.expander("显示设置", expanded=False):
        opacity = st.slider("原始观测透明度", 0.0, 1.0, 0.3, step=0.05, key="opacity")
    st.plotly_chart(signal_figure(frame.index, values, estimates, truth, opacity), width="stretch")
    if not estimates:
        st.info("请选择至少一种算法进行比较。当前显示原始观测及可用真值。")
        return
    st.subheader("任务指标")
    table = comparison_metrics(values, estimates, truth)
    st.dataframe(table, width="stretch", column_config={
        "RMSE": st.column_config.NumberColumn(format="%.4f"),
        "MAE": st.column_config.NumberColumn(format="%.4f"),
        "RPR": st.column_config.NumberColumn(format="%.4f"),
    })
    count = int(table["有效点数"].iloc[0])
    if count == 0:
        st.warning("所选方法没有共同有效点；请缩小窗口或增加样本数。指标中的空值不是零误差。")
    st.caption(f"所有方法及原始观测在相同的 {count} 个有效点上比较。MA 的空缺点不计入指标；其他方法的边界拟合和初始化区域仍计入。RPR 越低仅表示更平滑；常数参考或没有有效相邻点时显示空值。")
    with st.expander("误差与边界诊断", expanded=False):
        if truth is not None:
            st.plotly_chart(error_figure(frame.index, estimates, truth), width="stretch")
        else:
            st.write("没有真值，无法判断实际恢复误差。请结合曲线形状及应用目标判断效果。")
        for name, note in notes.items():
            st.markdown(f"**{name}**：{note}")
    with st.expander("算法原理与比较提示", expanded=False):
        st.markdown(
            "- **MA / EMA / Gaussian**：分别使用等权、指数权重、高斯权重进行平均。\n"
            "- **SavGol**：在局部窗口拟合多项式，兼顾降噪与局部形状。\n"
            "- **LOWESS**：局部线性回归，并根据残差降低异常值权重。\n"
            "- **Kalman**：结合随机游走模型预测与带噪观测，递推估计状态。\n\n"
            "窗口、σ 或平滑强度增大，可能同时损失峰值和快速变化。"
            "因果方法存在响应滞后的可能，离线方法借助未来数据，二者应结合实际使用方式比较。"
        )
