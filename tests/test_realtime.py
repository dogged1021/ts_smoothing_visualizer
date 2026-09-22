"""Arrival causality, target alignment, frozen publication and replay controls."""

import json
import re
import unittest
from unittest.mock import patch

import numpy as np
from streamlit.testing.v1 import AppTest

from tslab import algorithms
from tslab.data import ROOT
from tslab.realtime import CAUSAL_METHODS, DELAYED_METHODS, replay_signal


class ReplayTests(unittest.TestCase):
    def test_quadratic_targets_startup_and_delay(self) -> None:
        values = np.arange(20, dtype=float)**2
        for method, delay in (("SG-endpoint", 0), ("SG（固定延迟）", 2)):
            before, _, _ = replay_signal(values[:4], method)
            self.assertTrue(np.isnan(before).all())
            result, wait, startup = replay_signal(values[:5], method)
            self.assertEqual((wait, startup), (delay, 5))
            self.assertEqual(np.flatnonzero(np.isfinite(result)).tolist(), [4 - delay])
            self.assertAlmostEqual(result[4 - delay], values[4 - delay])
            result, _, _ = replay_signal(values, method)
            valid = np.isfinite(result)
            np.testing.assert_allclose(result[valid], values[valid], atol=1e-10)

    def test_published_outputs_never_change_and_future_is_unavailable(self) -> None:
        values = np.random.default_rng(7).normal(size=40)
        for method in CAUSAL_METHODS + DELAYED_METHODS:
            full, _, _ = replay_signal(values, method)
            for count in range(1, len(values)):
                prefix, _, _ = replay_signal(values[:count], method)
                valid = np.isfinite(prefix)
                np.testing.assert_allclose(prefix[valid], full[:count][valid])
                changed = values.copy()
                changed[count:] += 1000
                alternative, _, _ = replay_signal(changed, method)
                np.testing.assert_allclose(prefix[valid], alternative[:count][valid])

    def test_existing_causal_algorithms_and_centered_interior_match(self) -> None:
        values = np.random.default_rng(9).normal(size=41)
        expected = {
            "EMA": algorithms.exponential_average(values, adjust=False),
            "Kalman": algorithms.kalman_filter(values),
            "MA（后向）": algorithms.moving_average(values, 5, center=False),
            "SG（固定延迟）": algorithms.savitzky_golay(values, 5, 2),
        }
        for method, target in expected.items():
            result, _, _ = replay_signal(values, method)
            valid = np.isfinite(result)
            np.testing.assert_allclose(result[valid], target[valid], atol=1e-12)
        with self.assertRaises(ValueError):
            replay_signal(values, "SG-endpoint", window=4)


class ReplayAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        self.app.radio(key="mode").set_value("模拟实时").run()
        self.assertFalse(self.app.exception)

    def test_steps_reset_language_and_parameter_changes(self) -> None:
        self.assertEqual(self.app.slider(key="rt_count").value, 1)
        self.app.button(key="rt_jump").click().run()
        self.assertEqual(self.app.slider(key="rt_count").value, 11)
        metrics = self.app.dataframe[1].value.to_numpy()
        self.app.radio(key="language").set_value("en").run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.slider(key="rt_count").value, 11)
        np.testing.assert_array_equal(metrics, self.app.dataframe[1].value.to_numpy())
        for kind in ("caption", "title", "info"):
            for element in self.app.get(kind):
                self.assertIsNone(re.search(r"[\u4e00-\u9fff]", element.value), element.value)
        self.app.button(key="rt_step").click().run()
        self.assertEqual(self.app.slider(key="rt_count").value, 12)
        self.app.select_slider(key="rt_window").set_value(7).run()
        self.assertEqual(self.app.slider(key="rt_count").value, 1)
        self.app.button(key="rt_jump").click().run()
        self.app.button(key="rt_reset").click().run()
        self.assertEqual(self.app.slider(key="rt_count").value, 1)
        self.app.number_input(key="samples").set_value(3).run()
        self.app.slider(key="rt_count").set_value(3).run()
        self.assertFalse(self.app.exception)
        self.assertTrue(self.app.button(key="rt_step").disabled)

    def test_navigation_back_to_simulation_reinitializes_cleaned_widget(self) -> None:
        for destination in ("offline", "derivatives"):
            with self.subTest(destination=destination):
                self.setUp()
                self.app.button(key="rt_jump").click().run()
                if destination == "offline":
                    self.app.radio(key="mode").set_value("离线对比").run()
                else:
                    self.app.radio(key="application").set_value("导数与变化率估计").run()
                    self.app.radio(key="application").set_value("随机降噪与稳定读数").run()
                self.app.radio(key="mode").set_value("模拟实时").run()
                self.assertFalse(self.app.exception)
                self.assertEqual(self.app.slider(key="rt_count").value, 1)
                self.app.button(key="rt_step").click().run()
                self.assertFalse(self.app.exception)
                self.assertEqual(self.app.slider(key="rt_count").value, 2)
                self.app.button(key="rt_reset").click().run()
                self.assertEqual(self.app.slider(key="rt_count").value, 1)

    def test_arrived_prefix_only_empty_selection_and_real_data(self) -> None:
        with patch("tslab.applications.realtime_denoising.replay_signal", wraps=replay_signal) as run:
            self.app.button(key="rt_step").click().run()
            self.assertTrue(all(len(call.args[0]) == 2 for call in run.call_args_list))
        chart = json.loads(self.app.get("plotly_chart")[0].proto.spec)
        self.assertEqual(chart["layout"]["shapes"][0]["x0"], 0.1)
        self.app.multiselect(key="rt_causal").set_value([])
        self.app.multiselect(key="rt_delayed").set_value([]).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.dataframe), 0)
        self.app.selectbox(key="source").select("内置数据集").run()
        self.app.multiselect(key="rt_causal").set_value(list(CAUSAL_METHODS)).run()
        self.app.button(key="rt_jump").click().run()
        self.assertFalse(self.app.exception)
        self.assertNotIn("RMSE", self.app.dataframe[1].value.columns)
        self.app.radio(key="mode").set_value("离线对比").run()
        self.assertFalse(self.app.exception)


if __name__ == "__main__":
    unittest.main()
