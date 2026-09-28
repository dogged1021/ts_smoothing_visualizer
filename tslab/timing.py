"""Low-frequency delay relative to target timestamps, distinct from publication wait."""

import numpy as np
from scipy.signal import butter


def smoothing_timing(
    method: str, dt: float, *, window: int = 15, alpha: float = 0.1, sigma: float = 2.0,
    cutoff: float = 1.0, order: int = 2, process_variance: float = 0.05,
    observation_variance: float = 0.2, **unused: object,
) -> dict:
    """Describe DC group delay in samples/seconds; limits exclude initialization and edges.

    Inputs are already validated by the associated filter. Kalman uses its asymptotic
    scalar random-walk gain, not a fixed delay during startup. Unknown models remain NaN.
    """
    delay, wait = np.nan, 0.0
    note = "低频稳态近似；不代表所有频率或峰值的延迟。"
    if method == "MA（后向）":
        delay = (window - 1) / 2
    elif method in ("MA（居中）", "SavGol", "SG（固定延迟）", "Gaussian（固定延迟）"):
        delay, wait = 0.0, float(window // 2)
        note = "按目标时刻对齐；内部低频滞后为零，但仍需未来数据。"
    elif method == "Gaussian":
        delay, wait = 0.0, float(int(4 * sigma + 0.5))
        note = "按目标时刻对齐；内部低频滞后为零，但仍需未来数据。"
    elif method == "SG-endpoint":
        delay = 0.0
        note = "至少一阶拟合时低频极限为零；不保证快速变化无失真。"
    elif method == "Gaussian（单边）":
        ages = np.arange(window, dtype=float)
        weights = np.exp(-0.5 * (ages / sigma)**2)
        delay = float(weights @ ages / weights.sum())
    elif method == "EMA":
        delay = (1 - alpha) / alpha
        note = "EMA 稳态值；归一化权重与首值初始化阶段不适用。"
    elif method == "Butterworth（单向）":
        sos = butter(order, cutoff, fs=1 / dt, output="sos")
        # -d phase/dω at zero for each second-order section; sum cascade delays.
        b, a = sos[:, :3], sos[:, 3:]
        delay = float(np.sum((b[:, 1] + 2*b[:, 2]) / b.sum(axis=1)
                             - (a[:, 1] + 2*a[:, 2]) / a.sum(axis=1)))
    elif method == "Butterworth（双向）":
        delay, wait = 0.0, np.nan
        note = "全段离线；内部零相位不代表边界无误差或实时可用。"
    elif method == "Kalman":
        if process_variance > 0:
            prior = (process_variance + np.sqrt(process_variance**2 + 4*process_variance*observation_variance)) / 2
            gain = prior / (prior + observation_variance)
            delay = (1 - gain) / gain
            note = "仅当前随机游走模型的稳态增益近似；启动阶段不同。"
        else:
            note = "Q=0 时增益持续变化，无有限固定稳态滞后。"
    else:
        wait = np.nan
        note = "数据相关的局部稳健回归，无统一固定群延迟。"
    return {
        "未来等待（帧）": wait, "低频等效滞后（帧）": delay,
        "低频等效滞后（秒）": delay * dt, "理论值适用范围": note,
    }
