"""Replay only arrived observations, publishing each estimate once at its target index."""

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.signal import savgol_coeffs

from tslab.algorithms import _values

CAUSAL_METHODS = ("MA（后向）", "EMA", "Kalman", "SG-endpoint", "Gaussian（单边）")
DELAYED_METHODS = ("SG（固定延迟）", "Gaussian（固定延迟）")


def replay_signal(
    arrived: ArrayLike, method: str, *, window: int = 5, degree: int = 2,
    alpha: float = 0.1, sigma: float = 1.0, process_variance: float = 0.05, observation_variance: float = 0.2,
) -> tuple[NDArray[np.float64], int, int]:
    """Return target-aligned estimates, look-ahead frames and startup sample count.

    Replay a prefix sequentially. No boundary extrapolation or revision of published
    values is allowed. Replaying a longer prefix preserves all previously finite values.
    EMA uses fixed coefficients; Kalman matches the scalar batch filter initialization.
    """
    values = _values(arrived)
    if method not in CAUSAL_METHODS + DELAYED_METHODS:
        raise ValueError("未知的模拟方法。")
    windowed = method in ("MA（后向）", "SG-endpoint", "SG（固定延迟）", "Gaussian（单边）", "Gaussian（固定延迟）")
    if windowed and (not isinstance(window, (int, np.integer)) or window < 3 or window % 2 != 1):
        raise ValueError("模拟窗口必须是至少为 3 的奇数。")
    if method.startswith("SG") and (not isinstance(degree, (int, np.integer)) or not 0 <= degree < window):
        raise ValueError("SavGol 窗口必须为奇数，且多项式阶数必须为非负整数并小于窗口。")
    if method == "EMA" and (not np.isfinite(alpha) or not 0 < alpha <= 1):
        raise ValueError("alpha 必须在 (0, 1] 内。")
    if method == "Kalman" and (
        not np.isfinite([process_variance, observation_variance]).all()
        or process_variance < 0 or observation_variance <= 0
    ):
        raise ValueError("过程方差 Q 必须非负，观测方差 R 必须大于 0。")
    if method.startswith("Gaussian") and (not np.isfinite(sigma) or sigma <= 0):
        raise ValueError("sigma 必须大于 0。")
    delay = window // 2 if method in DELAYED_METHODS else 0
    startup = window if windowed else 1
    coefficients = None
    if method.startswith("SG"):
        coefficients = savgol_coeffs(window, degree, pos=window - 1 - delay, use="dot")
    if method.startswith("Gaussian"):
        offsets = np.arange(window, dtype=float) - (window - 1 - delay)
        coefficients = np.exp(-0.5 * (offsets / sigma)**2)
        coefficients /= coefficients.sum()
    output = np.full(len(values), np.nan)
    mean, variance = values[0], 1.0
    for arrival, value in enumerate(values):
        if arrival + 1 < startup:
            continue
        if method == "EMA":
            mean = value if arrival == 0 else alpha * value + (1 - alpha) * mean
        elif method == "Kalman":
            if arrival:
                variance += process_variance
            gain = variance / (variance + observation_variance)
            mean += gain * (value - mean)
            variance *= 1 - gain
        else:
            samples = values[arrival - window + 1:arrival + 1]
            mean = float(np.mean(samples) if coefficients is None else coefficients @ samples)
        output[arrival - delay] = mean
    return output, delay, startup


def replay_derivatives(
    arrived: ArrayLike, method: str, dt: float, *, window: int = 5, degree: int = 2, alpha: float = 0.1,
) -> tuple[dict[str, NDArray[np.float64]], int, dict[str, int]]:
    """Publish signal and derivatives at their target times, without endpoint extrapolation."""
    values = _values(arrived)
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("采样间隔必须大于 0。")
    if method in ("SG-endpoint", "SG（固定延迟）"):
        if not isinstance(degree, (int, np.integer)) or degree < 2:
            raise ValueError("同时估计一阶和二阶导数时，多项式阶数至少为 2。")
        signal, delay, startup = replay_signal(values, method, window=window, degree=degree)
        result = {"signal": signal}
        for order, key in ((1, "d1"), (2, "d2")):
            coefficients = savgol_coeffs(window, degree, deriv=order, delta=dt,
                                         pos=window - 1 - delay, use="dot")
            output = np.full(len(values), np.nan)
            for arrival in range(window - 1, len(values)):
                output[arrival - delay] = coefficients @ values[arrival - window + 1:arrival + 1]
            result[key] = output
        return result, delay, {key: startup for key in result}
    if method not in ("后向差分", "EMA 后向差分"):
        raise ValueError("未知的模拟方法。")
    signal = replay_signal(values, "EMA", alpha=alpha)[0] if method == "EMA 后向差分" else values.copy()
    # A prefix of one or two observations is valid, but cannot yet publish derivatives.
    result = {"signal": signal, "d1": np.full(len(values), np.nan), "d2": np.full(len(values), np.nan)}
    for arrival in range(2, len(signal)):
        previous, last, current = signal[arrival - 2:arrival + 1]
        result["d1"][arrival] = (3 * current - 4 * last + previous) / (2 * dt)
        result["d2"][arrival] = (current - 2 * last + previous) / dt**2
    return result, 0, {"signal": 1, "d1": 3, "d2": 3}
