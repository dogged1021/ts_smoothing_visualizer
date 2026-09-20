"""Evaluate estimates on the same available samples without closing gaps."""

import numpy as np
import pandas as pd
from numpy.typing import NDArray


def comparison_metrics(
    observed: NDArray[np.float64],
    estimates: dict[str, NDArray[np.float64]],
    truth: NDArray[np.float64] | None = None,
) -> pd.DataFrame:
    """Report errors on common finite points and RPR on adjacent valid pairs.

    RPR is undefined for a constant reference or when no adjacent pairs exist.
    Missing truth omits RMSE/MAE entirely. An empty common interval returns NaNs.
    """
    observed = np.asarray(observed, dtype=float)
    if observed.ndim != 1:
        raise ValueError("观测必须是一维数组。")
    curves = {"原始观测": observed, **estimates}
    valid = np.isfinite(observed)
    for values in curves.values():
        if np.asarray(values).shape != observed.shape:
            raise ValueError("输出长度必须与观测一致。")
        valid &= np.isfinite(values)
    if truth is not None:
        truth = np.asarray(truth, dtype=float)
        if truth.shape != observed.shape:
            raise ValueError("真值长度必须与观测一致。")
        valid &= np.isfinite(truth)
    pairs = valid[:-1] & valid[1:]
    variation = np.abs(np.diff(observed))[pairs].sum()
    rows = []
    for name, values in curves.items():
        values = np.asarray(values, dtype=float)
        row = {"方法": name, "有效点数": int(valid.sum())}
        if truth is not None:
            error = values[valid] - truth[valid]
            row["RMSE"] = float(np.sqrt(np.mean(error**2))) if error.size else np.nan
            row["MAE"] = float(np.mean(np.abs(error))) if error.size else np.nan
        row["RPR"] = float(np.abs(np.diff(values))[pairs].sum() / variation) if variation > 0 else np.nan
        rows.append(row)
    return pd.DataFrame(rows).set_index("方法")
