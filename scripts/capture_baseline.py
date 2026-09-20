"""Capture the original app's outputs before refactoring (run in ts_filter)."""

import argparse
import base64
import hashlib
import json
import os
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    "Sunspots": "sunspots",
    "Noisy Sine": "noisy_sine",
    "Humidity": "long_term_weather_rh",
    "Wind Speed": "long_term_weather_wv",
    "Process Anomalies": "process_anomalies",
}


def decode_values(values: list | dict) -> np.ndarray:
    """Read a one-dimensional Plotly JSON array, including binary encoding."""
    if isinstance(values, dict):
        return np.frombuffer(base64.b64decode(values["bdata"]), dtype=values["dtype"])
    return np.asarray(values, dtype=float)


def main() -> None:
    """Save numerical references and observed interaction outcomes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New snapshot directory; existing files are refused.")
    output = parser.parse_args().output.resolve()
    if output.exists():
        parser.error("Choose a new output directory to preserve existing snapshots.")
    os.chdir(ROOT)
    report = {
        "python": platform.python_version(),
        "dependencies": {p: version(p) for p in ("streamlit", "pandas", "numpy", "scipy", "plotly", "statsmodels", "pykalman")},
        "app_sha256": hashlib.sha256((ROOT / "app.py").read_bytes()).hexdigest(),
        "datasets": {},
        "interactions": {},
    }
    arrays = {}
    app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
    assert not app.exception, [e.message for e in app.exception]
    report["default_sliders"] = {s.key or s.label: s.value for s in app.slider}
    report["default_selection"] = {c.key: c.value for c in app.checkbox}

    for label, stem in DATASETS.items():
        app.selectbox[0].select(label)
        for checkbox in app.checkbox:
            checkbox.check()
        app.run()
        assert not app.exception, [e.message for e in app.exception]
        frame = pd.read_csv(ROOT / "data" / f"{stem}.csv", parse_dates=["timestamp"])
        chart = json.loads(app.get("plotly_chart")[0].proto.spec)
        assert len(chart["data"]) == 7
        traces = {}
        for trace in chart["data"]:
            values = decode_values(trace["y"])
            assert len(values) == len(frame), (stem, trace["name"], len(values))
            assert np.isfinite(values).all(), (stem, trace["name"])
            arrays[f"{stem}__{trace['name']}"] = values
            traces[trace["name"]] = {"first": float(values[0]), "last": float(values[-1]), "mean": float(values.mean())}
        intervals = frame["timestamp"].diff().dropna().dt.total_seconds()
        report["datasets"][stem] = {
            "rows": len(frame),
            "csv_sha256": hashlib.sha256((ROOT / "data" / f"{stem}.csv").read_bytes()).hexdigest(),
            "missing_values": int(frame.isna().sum().sum()),
            "duplicate_timestamps": int(frame["timestamp"].duplicated().sum()),
            "strictly_increasing": bool((intervals > 0).all()),
            "sampling_intervals_seconds": intervals.unique().tolist(),
            "traces": traces,
            "displayed_rpr": app.dataframe[0].value.to_dict(),
        }

    for checkbox in app.checkbox:
        checkbox.uncheck()
    app.run()
    assert not app.exception
    report["interactions"]["all_unchecked"] = {
        "chart_traces": len(json.loads(app.get("plotly_chart")[0].proto.spec)["data"]),
        "metric_columns": len(app.dataframe[0].value.columns),
    }
    app.slider(key="sg_win").set_value(5)
    app.slider(key="sg_poly").set_value(5)
    app.run()
    report["interactions"]["savgol_window_5_poly_5_unchecked"] = [e.message for e in app.exception]

    app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
    app.slider[0].set_value(50)
    app.slider(key="sg_win").set_value(51)
    app.run()
    report["interactions"]["savgol_window_51_length_50_unchecked"] = [e.message for e in app.exception]

    output.mkdir(parents=True)
    np.savez_compressed(output / "curves.npz", **arrays)
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Captured {len(arrays)} curves from {len(DATASETS)} datasets in {output}")
    print(json.dumps(report["interactions"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
