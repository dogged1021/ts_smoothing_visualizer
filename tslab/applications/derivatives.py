"""A07: derivative estimation, with analytic truth and explicit boundary evaluation."""

from functools import partial

import numpy as np
import streamlit as st
from numpy.typing import NDArray

from tslab import algorithms
from tslab.applications import realtime_derivatives
from tslab.data import DERIVATIVE_SCENARIOS, derivative_signal
from tslab.i18n import translate
from tslab.metrics import derivative_metrics
from tslab.plotting import DERIVATIVE_COLORS, derivative_figure
from tslab.ui import odd_window


def _method_controls(
    name: str, values: NDArray[np.float64], dt: float, causal: bool, language: str, sigma: float = 2.0
) -> tuple[dict[str, NDArray[np.float64]], tuple[int, int]]:
    t = partial(translate, language=language)
    boundary = (2, 0) if causal else (1, 1)
    if name == "直接差分":
        return algorithms.finite_differences(values, dt, backward=causal), boundary
    with st.expander(t("{name} · 参数", name=t(name)), expanded=False):
        if name == "EMA 后差分":
            alpha = st.slider(t("平滑因子 α"), 0.01, 1.0, 0.1, 0.01, key="d_ema_alpha")
            st.caption(t("EMA 使用固定系数递推；启动影响仍计入评价，没有人为指定稳定时间。"))
            smooth = algorithms.exponential_average(values, alpha, adjust=False)
            return algorithms.finite_differences(smooth, dt, backward=causal), boundary
        if name == "Gaussian 后差分":
            smooth = algorithms.gaussian_average(values, sigma)
            margin = int(4 * sigma + 0.5) + 1
            return algorithms.finite_differences(smooth, dt), (margin, margin)
        if name == "Gaussian 导数核":
            radius = int(4 * sigma + 0.5)
            st.caption(t("直接以高斯零阶、一阶、二阶核卷积观测，并按 Δt 换算；边界范围为核半径。"))
            return algorithms.gaussian_derivatives(values, dt, sigma), (radius, radius)
        if name == "SavGol 直接求导":
            window = odd_window(t("窗口（样本）"), len(values), "d_sg_window")
            degrees = list(range(2, min(5, window - 1) + 1))
            if "d_sg_degree" in st.session_state and st.session_state["d_sg_degree"] not in degrees:
                st.session_state["d_sg_degree"] = degrees[-1]
            default = None if "d_sg_degree" in st.session_state else min(3, degrees[-1])
            degree = st.select_slider(t("多项式阶数"), options=degrees, value=default, key="d_sg_degree")
            st.caption(t("多项式阶数至少为 2；直接估计各阶导数，按真实 Δt 换算单位。端点使用多项式拟合。"))
            st.caption(t(
                "居中离线估计对齐窗口中心，不整体右移；若逐点获取数据，内部点需等待 {samples} 个未来样本"
                "（{delay:.3f} 秒）。端点另用多项式拟合。",
                samples=window // 2, delay=(window // 2) * dt,
            ))
            return algorithms.savgol_derivatives(values, dt, window, degree), (window // 2, window // 2)
    raise ValueError(t("未知算法：{name}", name=name))


def render(language: str = "zh", theme: str = "light") -> None:
    """Render the three derivative routes without mixing in unrelated application tasks."""
    t = partial(translate, language=language)
    st.title(t("导数与变化率估计"))
    st.caption(t("A07 · 比较信号、一阶导数和二阶导数。真值来自解析公式，不由带噪观测差分生成。"))
    processing = st.radio(t("处理方式"), ["离线对比", "模拟实时"], format_func=t, horizontal=True, key="d_processing")
    scenario = st.selectbox(t("实验场景"), DERIVATIVE_SCENARIOS, format_func=t, key="d_scenario")
    with st.expander(t("数据参数"), expanded=False):
        left, right = st.columns(2)
        samples = left.number_input(t("样本数"), min_value=3, max_value=2000, value=500, key="d_samples")
        dt = right.number_input(
            t("采样间隔 Δt（秒）"), min_value=0.001, max_value=1.0, value=0.05, format="%.3f", key="d_dt"
        )
        noise = left.slider(t("噪声标准差"), 0.0, 1.0, 0.05, step=0.01, key="d_noise")
        seed = right.number_input(t("随机种子"), min_value=0, max_value=1000000, value=42, key="d_seed")
    frame = derivative_signal(scenario, samples, dt, noise, seed)
    values = frame["value"].to_numpy()
    truth = {"signal": frame["truth"].to_numpy(), "d1": frame["d1"].to_numpy(), "d2": frame["d2"].to_numpy()}
    st.caption(t("时间单位为秒，幅值单位记为 u；一阶和二阶导数单位分别为 u/s、u/s²。"))
    if processing == "模拟实时":
        realtime_derivatives.render(frame, dt, language, theme)
        return
    left, right = st.columns(2)
    selected = left.multiselect(
        t("使用未来数据"), list(DERIVATIVE_COLORS), format_func=t,
        default=["直接差分", "SavGol 直接求导"], key="d_methods_offline",
    ) + right.multiselect(
        t("仅使用当前及过去数据"), ["后向差分", "EMA 后向差分"],
        format_func=t, default=[], key="d_methods_causal",
    )
    st.caption(t("离线差分采用三点中心公式，两端各一点为空缺；SavGol 和 Gaussian 使用未来样本。"))
    st.caption(t("因果模式使用三点后向差分：前两点为空缺；一阶公式为二阶精度，二阶公式为一阶精度。"))
    sigma = 2.0
    if any(name.startswith("Gaussian") for name in selected):
        with st.expander(t("Gaussian · 共用参数")):
            sigma = st.slider(t("σ（样本）"), 0.1, 10.0, 2.0, 0.1, key="d_sigma")
            st.caption(t("两条 Gaussian 路线共用 σ、4σ 截断与反射边界，零阶位置相同；直接导数核不等于平滑后差分。"))
            if "Gaussian 导数核" in selected:
                st.caption(t("采样与截断会产生导数偏差，尤其小 σ 时二阶核可能对常数产生非零输出；本实现保留库原始结果，不做矩修正。"))
    estimates = {}
    boundary = (0, 0)
    for name in selected:
        try:
            causal = name in ("后向差分", "EMA 后向差分")
            base = {"后向差分": "直接差分", "EMA 后向差分": "EMA 后差分"}.get(name, name)
            if name == "EMA 后向差分":
                with st.expander(t("{name} · 参数", name=t(name))):
                    alpha = st.slider(t("平滑因子 α"), 0.01, 1.0, 0.1, 0.01, key="d_backward_alpha")
                smooth = algorithms.exponential_average(values, alpha, adjust=False)
                result, margins = algorithms.finite_differences(smooth, dt, backward=True), (2, 0)
            else:
                result, margins = _method_controls(base, values, dt, causal, language, sigma)
            estimates[name] = result
            boundary = (max(boundary[0], margins[0]), max(boundary[1], margins[1]))
        except ValueError as error:
            st.warning(f"{t(name)}: {t(str(error))}")
    figure = derivative_figure(frame.index, values, truth, estimates, boundary, language=language, theme=theme)
    st.plotly_chart(figure, width="stretch", theme=None)
    st.caption(t("三行共享时间轴；点击图例可同时隐藏该方法的三条曲线。灰色区域标记所选方法的窗口边界或启动空缺。"))
    st.caption(t("原始观测以灰色线和前景采样点显示；直接差分的零阶信号就是原始观测，两者重合。"))
    if not estimates:
        st.info(t("请选择至少一种算法进行比较。当前显示原始观测及可用真值。"))
        return
    st.subheader(t("逐阶误差"))
    region = st.radio(
        t("评价范围"), ["排除窗口边界", "所有共同有效点"], format_func=t,
        horizontal=True, key="d_region",
    )
    mask = np.ones(samples, dtype=bool)
    if region == "排除窗口边界":
        left, right = boundary
        mask[:] = False
        if left + right < samples:
            mask[left:samples - right] = True
    table = derivative_metrics(truth, estimates, mask)
    display = table.copy()
    display["输出"] = display["输出"].map(t)
    display["方法"] = display["方法"].map(t)
    st.dataframe(display.rename(columns=t), hide_index=True, width="stretch", column_config={
        "RMSE": st.column_config.NumberColumn(format="%.6f"),
        "MAE": st.column_config.NumberColumn(format="%.6f"),
    })
    if (table["有效点数"] == 0).any():
        st.warning(t("所选方法没有共同有效点；请缩小窗口或增加样本数。指标中的空值不是零误差。"))
    st.caption(t("每一阶在相同的共同有效点上比较；不同阶量纲不同，不合并打分。EMA 初始化影响仍计入。"))
    with st.expander(t("算法原理与比较提示"), expanded=False):
        st.markdown(t(
            "**直接差分**用于展示噪声放大；**平滑后差分**先对观测降噪；"
            "**SavGol**从局部多项式直接计算导数。信号平滑得好，不代表导数误差小。"
        ))
        st.markdown(t(
            "正弦真值为 s(t)=sin(2πt/5)；多项式真值为 s(t)=0.1t²−0.5t+1。"
            "当前只使用光滑合成场景，不在阶跃等不可导点上计算点值导数误差。"
        ))
        st.markdown(t(
            "边界范围取已选方法的并集：中心差分为两端各 1 点，后向差分为前 2 点，"
            "SavGol 为两端各半个窗口，Gaussian 后差分为核半径加 1 点。"
            "切换评价范围可查看包含边界估计时的误差变化。"
        ))
