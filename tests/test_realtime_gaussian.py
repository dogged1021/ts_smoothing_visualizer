"""Gaussian replay weights, alignment and shared-window controls."""
import unittest
import numpy as np
from scipy.ndimage import gaussian_filter1d
from streamlit.testing.v1 import AppTest
from tslab.data import ROOT
from tslab.realtime import replay_signal


class GaussianReplayTests(unittest.TestCase):
    def test_centered_matches_explicit_radius_and_one_sided_ramp_lag(self):
        values = np.arange(20, dtype=float)
        centered, delay, startup = replay_signal(values, "Gaussian（固定延迟）")
        self.assertEqual((delay, startup), (2, 5))
        expected = gaussian_filter1d(values, 1.0, radius=2)
        np.testing.assert_allclose(centered[2:-2], expected[2:-2])
        self.assertTrue(np.isnan(centered[:2]).all() and np.isnan(centered[-2:]).all())
        one_sided, delay, startup = replay_signal(values, "Gaussian（单边）")
        weights = np.exp(-0.5 * np.arange(5)**2)
        weights /= weights.sum()
        np.testing.assert_allclose(one_sided[4:], values[4:] - weights @ np.arange(5))
        self.assertEqual((delay, startup), (0, 5))
        for method in ("Gaussian（单边）", "Gaussian（固定延迟）"):
            result, _, _ = replay_signal(np.ones(20), method)
            np.testing.assert_allclose(result[np.isfinite(result)], 1)
            early, _, _ = replay_signal(values[:4], method)
            self.assertTrue(np.isnan(early).all())
            with self.assertRaises(ValueError):
                replay_signal(values, method, sigma=0)

    def test_default_four_way_comparison_and_shared_parameters(self):
        app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        app.radio(key="mode").set_value("模拟实时").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.select_slider(key="rt_window").value, 5)
        self.assertEqual(app.slider(key="rt_sigma").value, 1.0)
        app.slider(key="rt_count").set_value(5).run()
        table = app.dataframe[0].value
        self.assertEqual(table["等待帧数"].tolist(), [0, 0, 2, 2])
        self.assertEqual(table["启动所需帧数"].tolist(), [5]*4)
        app.slider(key="rt_sigma").set_value(2.0).run()
        self.assertEqual(app.slider(key="rt_count").value, 1)
        app.radio(key="language").set_value("en").run()
        self.assertFalse(app.exception)
        self.assertIn("Gaussian (one-sided)", app.multiselect(key="rt_causal").options)
