"""Pure signal-processing functions. Window sizes are measured in samples."""

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from pykalman import KalmanFilter
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter
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
