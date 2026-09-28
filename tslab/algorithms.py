"""Pure signal-processing functions. Window sizes are measured in samples."""

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from pykalman import KalmanFilter
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, savgol_filter, sosfilt, sosfilt_zi, sosfiltfilt
from statsmodels.nonparametric.smoothers_lowess import lowess


def _values(values: ArrayLike) -> NDArray[np.float64]:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0 or not np.isfinite(array).all():
        raise ValueError("输入必须是一维、非空且不含缺失值或无穷值的数列。")
    return array


def _window(window: int, size: int) -> None:
    if not isinstance(window, (int, np.integer)) or not 1 <= window <= size:
        raise ValueError("窗口必须是正整数，且不能超过数据长度。")


def moving_average(values: ArrayLike, window: int = 15, *, center: bool = True) -> NDArray[np.float64]:
    """Average complete windows; return NaN where a complete window is unavailable."""
    array = _values(values)
    _window(window, len(array))
    return pd.Series(array).rolling(window, center=center).mean().to_numpy()


def exponential_average(values: ArrayLike, alpha: float = 0.1, *, adjust: bool = True) -> NDArray[np.float64]:
    """Use normalized historical weights by default, matching the original app."""
    array = _values(values)
    if not np.isfinite(alpha) or not 0 < alpha <= 1:
        raise ValueError("alpha 必须在 (0, 1] 内。")
    return pd.Series(array).ewm(alpha=alpha, adjust=adjust).mean().to_numpy()


def savitzky_golay(values: ArrayLike, window: int = 15, degree: int = 2) -> NDArray[np.float64]:
    """Fit local polynomials, using SciPy's interpolation at the endpoints."""
    array = _values(values)
    _window(window, len(array))
    if window % 2 != 1 or not isinstance(degree, (int, np.integer)) or not 0 <= degree < window:
        raise ValueError("SavGol 窗口必须为奇数，且多项式阶数必须为非负整数并小于窗口。")
    return savgol_filter(array, window_length=window, polyorder=degree, mode="interp")


def local_regression(values: ArrayLike, fraction: float = 0.05) -> NDArray[np.float64]:
    """Apply robust LOWESS against sample index, preserving three reweighting passes."""
    array = _values(values)
    if not np.isfinite(fraction) or not 0 < fraction <= 1 or int(fraction * len(array)) < 2:
        raise ValueError("LOWESS 邻域至少需要 2 个样本，frac 应在 (0, 1] 内。")
    return lowess(array, np.arange(len(array)), frac=fraction, it=3, return_sorted=False)


def gaussian_average(values: ArrayLike, sigma: float = 2.0) -> NDArray[np.float64]:
    """Apply a Gaussian kernel with reflective boundaries and four-sigma truncation."""
    array = _values(values)
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma 必须大于 0。")
    return gaussian_filter1d(array, sigma=sigma, mode="reflect", truncate=4.0)


def kalman_filter(
    values: ArrayLike, process_variance: float = 0.05, observation_variance: float = 0.2
) -> NDArray[np.float64]:
    """Filter a scalar random walk; Q and R are variances, not standard deviations."""
    array = _values(values)
    if (
        not np.isfinite([process_variance, observation_variance]).all()
        or process_variance < 0
        or observation_variance <= 0
    ):
        raise ValueError("过程方差 Q 必须非负，观测方差 R 必须大于 0。")
    model = KalmanFilter(
        transition_matrices=[1],
        observation_matrices=[1],
        initial_state_mean=array[0],
        initial_state_covariance=1,
        transition_covariance=process_variance,
        observation_covariance=observation_variance,
    )
    means, _ = model.filter(array)
    return means[:, 0]


def finite_differences(
    values: ArrayLike, dt: float, *, backward: bool = False
) -> dict[str, NDArray[np.float64]]:
    """Estimate derivatives at the sample times; incomplete stencils remain NaN.

    Offline: centered three-point first and second derivatives.
    Causal: three-point backward derivatives (second-order accurate d1,
    first-order accurate d2). Both backward stencils are exact for quadratics.
    """
    array = _values(values)
    if len(array) < 3:
        raise ValueError("导数估计至少需要 3 个样本。")
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("采样间隔必须大于 0。")
    d1 = np.full(len(array), np.nan)
    d2 = np.full(len(array), np.nan)
    second = (array[2:] - 2 * array[1:-1] + array[:-2]) / dt**2
    if backward:
        d1[2:] = (3 * array[2:] - 4 * array[1:-1] + array[:-2]) / (2 * dt)
        d2[2:] = second
    else:
        d1[1:-1] = (array[2:] - array[:-2]) / (2 * dt)
        d2[1:-1] = second
    return {"signal": array.copy(), "d1": d1, "d2": d2}


def savgol_derivatives(
    values: ArrayLike, dt: float, window: int = 15, degree: int = 3
) -> dict[str, NDArray[np.float64]]:
    """Estimate signal and its first two derivatives with local polynomial fits."""
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("采样间隔必须大于 0。")
    if degree < 2:
        raise ValueError("同时估计一阶和二阶导数时，多项式阶数至少为 2。")
    signal = savitzky_golay(values, window, degree)
    array = _values(values)
    return {
        "signal": signal,
        "d1": savgol_filter(array, window, degree, deriv=1, delta=dt, mode="interp"),
        "d2": savgol_filter(array, window, degree, deriv=2, delta=dt, mode="interp"),
    }


def gaussian_derivatives(values: ArrayLike, dt: float, sigma: float = 2.0) -> dict[str, NDArray[np.float64]]:
    """Apply sampled Gaussian derivative kernels, with time-unit scaling and reflective edges.

    Keep SciPy's raw truncated kernels: do not silently correct their discrete moments.
    In particular, the second derivative can leak a constant offset, especially for small sigma.
    """
    array = _values(values)
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("采样间隔必须大于 0。")
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma 必须大于 0。")
    return {
        key: gaussian_filter1d(array, sigma=sigma, order=order, mode="reflect", truncate=4.0) / dt**order
        for order, key in enumerate(("signal", "d1", "d2"))
    }


def butterworth_lowpass(
    values: ArrayLike, dt: float, cutoff: float, order: int = 2, *, zero_phase: bool = False,
) -> NDArray[np.float64]:
    """Filter in SOS form, using first-sample steady state or offline forward/backward filtering."""
    array = _values(values)
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("采样间隔必须大于 0。")
    if not np.isfinite(cutoff) or not 0 < cutoff < 0.5 / dt:
        raise ValueError("截止频率必须大于 0 且小于 Nyquist 频率。")
    if not isinstance(order, (int, np.integer)) or not 1 <= order <= 8:
        raise ValueError("Butterworth 阶数必须为 1 到 8 的整数。")
    sos = butter(order, cutoff, btype="lowpass", fs=1 / dt, output="sos")
    if zero_phase:
        padlen = 3 * (order + 1)
        if len(array) <= padlen:
            raise ValueError("双向 Butterworth 数据不足；请增加样本数或降低阶数。")
        return sosfiltfilt(sos, array, padtype="odd", padlen=padlen)
    return sosfilt(sos, array, zi=sosfilt_zi(sos) * array[0])[0]
