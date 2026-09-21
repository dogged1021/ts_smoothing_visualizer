"""Load bundled observations and generate reproducible signals with known truth."""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    "太阳黑子 · Sunspots": "sunspots",
    "带噪正弦 · Noisy Sine": "noisy_sine",
    "湿度 · Humidity": "long_term_weather_rh",
    "风速 · Wind Speed": "long_term_weather_wv",
    "过程异常 · Process Anomalies": "process_anomalies",
}
SCENARIOS = ("正弦信号", "缓慢趋势", "恒定读数")
DERIVATIVE_SCENARIOS = ("正弦信号", "二次多项式")


def validate_data(frame: pd.DataFrame) -> float:
    """Check complete, uniform samples and return the interval in seconds."""
    if "value" not in frame or len(frame) < 2:
        raise ValueError("数据至少需要两行，并包含 value 列。")
    values = frame["value"].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("观测包含缺失值或无穷值；当前阶段不自动插补。")
    if isinstance(frame.index, pd.DatetimeIndex):
        if frame.index.hasnans:
            raise ValueError("时间戳包含缺失值。")
        times = (frame.index - frame.index[0]).total_seconds().to_numpy()
    else:
        times = frame.index.to_numpy(dtype=float)
    intervals = np.diff(times)
    if not np.isfinite(times).all() or not (intervals > 0).all():
        raise ValueError("时间必须严格递增，且不含重复或无效时间戳。")
    if not np.allclose(intervals, intervals[0], rtol=1e-6, atol=1e-9):
        raise ValueError("当前板块要求等间隔采样；非均匀采样处理将在后续阶段提供。")
    return float(intervals[0])


def load_dataset(stem: str) -> pd.DataFrame:
    """Load a known CSV regardless of the process's working directory."""
    if stem not in DATASETS.values():
        raise ValueError("未知的内置数据集。")
    frame = pd.read_csv(ROOT / "data" / f"{stem}.csv", parse_dates=["timestamp"]).set_index("timestamp")
    validate_data(frame)
    return frame


def synthetic_signal(
    scenario: str, samples: int = 500, dt: float = 0.1, noise: float = 0.3, seed: int = 42
) -> pd.DataFrame:
    """Generate observations and clean truth on a time axis measured in seconds."""
    if not isinstance(samples, (int, np.integer)) or samples < 2:
        raise ValueError("样本数必须是至少为 2 的整数。")
    if not np.isfinite([dt, noise]).all() or dt <= 0 or noise < 0:
        raise ValueError("采样间隔必须大于 0，噪声标准差必须非负。")
    time = np.arange(samples) * dt
    if scenario == "正弦信号":
        truth = np.sin(2 * np.pi * time / 5)
    elif scenario == "缓慢趋势":
        truth = 0.03 * time + 0.5 * np.sin(2 * np.pi * time / 30)
    elif scenario == "恒定读数":
        truth = np.ones(samples)
    elif scenario == "二次多项式":
        truth = 0.1 * time**2 - 0.5 * time + 1
    else:
        raise ValueError("未知的合成场景。")
    values = truth + np.random.default_rng(seed).normal(0, noise, samples)
    return pd.DataFrame({"value": values, "truth": truth}, index=pd.Index(time, name="时间（s）"))


def derivative_signal(
    scenario: str, samples: int = 500, dt: float = 0.05, noise: float = 0.05, seed: int = 42
) -> pd.DataFrame:
    """Add analytic derivative truth, in u/s and u/s², to a synthetic signal."""
    if scenario not in DERIVATIVE_SCENARIOS:
        raise ValueError("未知的导数实验场景。")
    frame = synthetic_signal(scenario, samples, dt, noise, seed)
    time = frame.index.to_numpy()
    if scenario == "正弦信号":
        omega = 2 * np.pi / 5
        frame["d1"] = omega * np.cos(omega * time)
        frame["d2"] = -(omega**2) * np.sin(omega * time)
    else:
        frame["d1"] = 0.2 * time - 0.5
        frame["d2"] = 0.2
    return frame
