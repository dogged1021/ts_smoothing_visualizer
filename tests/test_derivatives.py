"""Analytic derivative accuracy, time scaling, causality and A07 interactions."""

import json
import re
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from tslab import algorithms as alg
from tslab.data import ROOT, derivative_signal
from tslab.metrics import derivative_metrics
from tslab.plotting import DERIVATIVE_COLORS, derivative_figure


class DerivativeNumericsTests(unittest.TestCase):
    def test_analytic_truth_and_reproducible_noise(self) -> None:
        frame = derivative_signal("正弦信号", samples=51, dt=0.1, seed=3)
        pd.testing.assert_frame_equal(frame, derivative_signal("正弦信号", samples=51, dt=0.1, seed=3))
        omega = 2 * np.pi / 5
        np.testing.assert_allclose(frame["d1"], omega * np.cos(omega * frame.index))
        np.testing.assert_allclose(frame["d2"], -omega**2 * np.sin(omega * frame.index))

    def test_quadratic_derivatives_are_exact_on_valid_samples(self) -> None:
        for dt in (0.02, 0.3):
            frame = derivative_signal("二次多项式", samples=51, dt=dt, noise=0)
            values = frame["value"].to_numpy()
            outputs = [
                alg.finite_differences(values, dt),
                alg.finite_differences(values, dt, backward=True),
                alg.savgol_derivatives(values, dt, window=7, degree=2),
            ]
            for result in outputs:
                for key in ("d1", "d2"):
                    valid = np.isfinite(result[key])
                    np.testing.assert_allclose(result[key][valid], frame[key].to_numpy()[valid], atol=1e-9)
            self.assertTrue(np.isnan(outputs[0]["d1"][[0, -1]]).all())
            self.assertTrue(np.isnan(outputs[1]["d2"][:2]).all())
            self.assertTrue(np.isfinite(outputs[2]["d2"]).all())

    def test_derivatives_scale_with_actual_time_interval(self) -> None:
        values = np.sin(np.arange(51) / 7)
        for method in (alg.finite_differences, alg.savgol_derivatives):
            first, second = method(values, 0.1), method(values, 0.2)
            np.testing.assert_allclose(first["signal"], second["signal"])
            np.testing.assert_allclose(second["d1"], first["d1"] / 2, equal_nan=True)
            np.testing.assert_allclose(second["d2"], first["d2"] / 4, equal_nan=True)

    def test_causal_derivative_pipelines_ignore_future_observations(self) -> None:
        values = np.random.default_rng(2).normal(size=80)
        changed = values.copy()
        changed[40:] += 200
        for smooth in (lambda x: x, lambda x: alg.exponential_average(x, adjust=False)):
            first = alg.finite_differences(smooth(values), 0.1, backward=True)
            second = alg.finite_differences(smooth(changed), 0.1, backward=True)
            for key in first:
                np.testing.assert_allclose(first[key][:40], second[key][:40], equal_nan=True)

    def test_savgol_reduces_derivative_noise_in_fixed_sine_experiment(self) -> None:
        frame = derivative_signal("正弦信号")
        values = frame["value"].to_numpy()
        raw = alg.finite_differences(values, 0.05)
        smooth = alg.savgol_derivatives(values, 0.05)
        for key in ("d1", "d2"):
            target = frame[key].to_numpy()[7:-7]
            self.assertLess(np.mean((smooth[key][7:-7] - target)**2), np.mean((raw[key][7:-7] - target)**2))

    def test_metrics_respect_per_order_validity_and_boundary_mask(self) -> None:
        truth = {key: np.zeros(5) for key in ("signal", "d1", "d2")}
        result = {key: np.array([10.0, 0, 0, 0, 10]) for key in truth}
        result["d1"][[0, -1]] = np.nan
        table = derivative_metrics(truth, {"test": result})
        self.assertEqual(table["有效点数"].tolist(), [5, 3, 5])
        interior = derivative_metrics(truth, {"test": result}, np.array([False, True, True, True, False]))
        self.assertTrue((interior["RMSE"] == 0).all())
        empty = derivative_metrics(truth, {"test": result}, np.zeros(5, dtype=bool))
        self.assertTrue(empty["RMSE"].isna().all())
        self.assertTrue((empty["有效点数"] == 0).all())

    def test_invalid_derivative_inputs(self) -> None:
        for run in (
            lambda: alg.finite_differences([1, 2], 1),
            lambda: alg.finite_differences([1, 2, 3], 0),
            lambda: alg.savgol_derivatives(np.ones(15), np.nan),
            lambda: alg.savgol_derivatives(np.ones(15), 0.1, degree=1),
        ):
            with self.assertRaises(ValueError):
                run()

    def test_linked_panels_colors_and_dark_theme(self) -> None:
        frame = derivative_signal("正弦信号", samples=31)
        truth = {"signal": frame["truth"].to_numpy(), "d1": frame["d1"].to_numpy(), "d2": frame["d2"].to_numpy()}
        estimates = {"直接差分": alg.finite_differences(frame["value"].to_numpy(), 0.05)}
        figure = derivative_figure(frame.index, frame["value"].to_numpy(), truth, estimates, (1, 1),
                                   language="en", theme="dark")
        observed = figure.data[0]
        self.assertEqual(observed.name, "Observations")
        np.testing.assert_array_equal(observed.y, frame["value"].to_numpy())
        self.assertIn("markers", observed.mode)
        self.assertGreater(observed.zorder, max(trace.zorder or 0 for trace in figure.data[1:]))
        self.assertEqual(figure.layout.xaxis.matches, "x3")
        self.assertEqual(figure.layout.xaxis2.matches, "x3")
        self.assertEqual(figure.layout.yaxis3.title.text, "Second derivative (u/s²)")
        self.assertEqual(figure.layout.font.color, "#E7EDF5")
        traces = [trace for trace in figure.data if trace.legendgroup == "直接差分"]
        self.assertEqual(len(traces), 3)
        self.assertEqual(len({trace.line.color for trace in traces}), 1)
        self.assertEqual(sum(bool(trace.showlegend) for trace in traces), 1)


class DerivativeAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        self.app.radio(key="application").set_value("导数与变化率估计").run()
        self.assertFalse(self.app.exception)

    def test_all_routes_language_and_parameter_preservation(self) -> None:
        self.app.multiselect[0].set_value(list(DERIVATIVE_COLORS)).run()
        self.app.selectbox(key="d_scenario").select("二次多项式")
        self.app.number_input(key="d_dt").set_value(0.1)
        self.app.select_slider(key="d_sg_window").set_value(9)
        self.app.run()
        self.assertFalse(self.app.exception)
        before = self.app.dataframe[0].value.copy()
        self.assertEqual(len(before), 12)
        chart = json.loads(self.app.get("plotly_chart")[0].proto.spec)
        self.assertEqual(len(chart["data"]), 16)
        self.app.radio(key="language").set_value("en").run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.select_slider(key="d_sg_window").value, 9)
        self.assertEqual(self.app.number_input(key="d_dt").value, 0.1)
        np.testing.assert_array_equal(before.iloc[:, 2:].to_numpy(), self.app.dataframe[0].value.iloc[:, 2:].to_numpy())
        for kind in ("caption", "markdown", "title", "subheader"):
            for element in self.app.get(kind):
                self.assertIsNone(re.search(r"[\u4e00-\u9fff]", element.value), element.value)
        self.app.radio(key="language").set_value("zh").run()
        pd.testing.assert_frame_equal(before, self.app.dataframe[0].value)

    def test_short_data_empty_interior_and_all_valid_region(self) -> None:
        self.app.multiselect[0].set_value(list(DERIVATIVE_COLORS)).run()
        self.app.select_slider(key="d_sg_degree").set_value(5).run()
        self.app.number_input(key="d_samples").set_value(3).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.select_slider(key="d_sg_degree").value, 2)
        self.assertTrue((self.app.dataframe[0].value["有效点数"] == 0).all())
        self.assertTrue(any("没有共同有效点" in w.value for w in self.app.warning))
        self.app.radio(key="d_region").set_value("所有共同有效点").run()
        self.assertTrue((self.app.dataframe[0].value["有效点数"] > 0).all())
        self.assertFalse(self.app.exception)

    def test_causal_filter_empty_selection_and_navigation(self) -> None:
        with patch("tslab.algorithms.savgol_derivatives", side_effect=AssertionError("Noncausal method executed")):
            self.app.multiselect(key="d_methods_offline").set_value([])
            self.app.multiselect(key="d_methods_causal").set_value(["后向差分", "EMA 后向差分"]).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.multiselect(key="d_methods_causal").options, ["后向差分", "EMA 后向差分"])
        self.app.multiselect(key="d_methods_causal").set_value([]).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.dataframe), 0)
        self.assertEqual(len(self.app.get("plotly_chart")), 1)
        self.app.radio(key="application").set_value("随机降噪与稳定读数").run()
        self.assertFalse(self.app.exception)
        self.assertIn("RPR", self.app.dataframe[0].value.columns)


if __name__ == "__main__":
    unittest.main()
