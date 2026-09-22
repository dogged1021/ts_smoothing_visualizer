"""Derivative replay alignment, availability and cross-application navigation."""

import unittest
from unittest.mock import patch

import numpy as np
from streamlit.testing.v1 import AppTest

from tslab import algorithms
from tslab.data import ROOT
from tslab.realtime import replay_derivatives

METHODS = ["后向差分", "EMA 后向差分", "SG-endpoint", "SG（固定延迟）"]


class DerivativeReplayTests(unittest.TestCase):
    def test_polynomial_alignment_and_time_scaling(self) -> None:
        for dt in (0.05, 0.3):
            time = np.arange(25) * dt
            values = time**2
            for method in ("后向差分", "SG-endpoint", "SG（固定延迟）"):
                result, delay, starts = replay_derivatives(values, method, dt)
                for key, target in (("signal", values), ("d1", 2 * time), ("d2", np.full(25, 2))):
                    valid = np.isfinite(result[key])
                    np.testing.assert_allclose(result[key][valid], target[valid], atol=1e-9)
                    self.assertEqual(np.flatnonzero(valid)[0], starts[key] - 1 - delay)
                    self.assertEqual(np.flatnonzero(valid)[-1], 24 - delay)

    def test_prefixes_freeze_published_values_and_handle_startup(self) -> None:
        values = np.random.default_rng(3).normal(size=20)
        for method in METHODS:
            full, _, _ = replay_derivatives(values, method, 0.1)
            for count in range(1, 20):
                prefix, _, _ = replay_derivatives(values[:count], method, 0.1)
                changed = values.copy()
                changed[count:] += 100
                alternative, _, _ = replay_derivatives(changed, method, 0.1)
                for key in prefix:
                    valid = np.isfinite(prefix[key])
                    np.testing.assert_allclose(prefix[key][valid], full[key][:count][valid])
                    np.testing.assert_allclose(prefix[key][valid], alternative[key][:count][valid])
                if count < 3:
                    self.assertTrue(np.isnan(prefix["d1"]).all())
                    self.assertTrue(np.isnan(prefix["d2"]).all())
        expected = algorithms.finite_differences(algorithms.exponential_average(values, adjust=False), 0.1, backward=True)
        actual, _, _ = replay_derivatives(values, "EMA 后向差分", 0.1)
        for key in expected:
            np.testing.assert_allclose(actual[key], expected[key], equal_nan=True)
        for dt, degree in ((0, 2), (0.1, 1)):
            with self.assertRaises(ValueError):
                replay_derivatives(values, "SG-endpoint", dt, degree=degree)


class DerivativeReplayAppTests(unittest.TestCase):
    def test_controls_short_sequences_language_and_navigation(self) -> None:
        app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        app.radio(key="application").set_value("导数与变化率估计").run()
        app.radio(key="d_processing").set_value("模拟实时").run()
        self.assertFalse(app.exception)
        app.multiselect(key="dr_causal").set_value(METHODS[:3]).run()
        with patch("tslab.applications.realtime_derivatives.replay_derivatives", wraps=replay_derivatives) as run:
            app.button(key="dr_step").click().run()
            self.assertTrue(all(len(call.args[0]) == 2 for call in run.call_args_list))
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe[0].value), 12)
        app.button(key="dr_jump").click().run()
        before = app.dataframe[1].value.iloc[:, 2:].to_numpy()
        app.radio(key="language").set_value("en").run()
        self.assertEqual(app.slider(key="dr_count").value, 12)
        np.testing.assert_array_equal(before, app.dataframe[1].value.iloc[:, 2:].to_numpy())
        app.number_input(key="d_samples").set_value(3).run()
        self.assertEqual(app.slider(key="dr_count").value, 1)
        app.slider(key="dr_count").set_value(3).run()
        self.assertTrue(app.button(key="dr_step").disabled)
        app.radio(key="d_processing").set_value("离线对比").run()
        app.radio(key="d_processing").set_value("模拟实时").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.slider(key="dr_count").value, 1)
        app.radio(key="application").set_value("随机降噪与稳定读数").run()
        app.radio(key="mode").set_value("模拟实时").run()
        app.button(key="rt_jump").click().run()
        app.radio(key="application").set_value("导数与变化率估计").run()
        app.radio(key="d_processing").set_value("模拟实时").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.slider(key="dr_count").value, 1)
        app.multiselect(key="dr_causal").set_value([])
        app.multiselect(key="dr_delayed").set_value([]).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe), 0)


if __name__ == "__main__":
    unittest.main()
