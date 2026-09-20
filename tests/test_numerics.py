"""Numerical regression and edge cases, runnable with the standard library."""

import os
import tempfile
import unittest

import numpy as np
import pandas as pd

from tslab import algorithms as alg
from tslab.data import DATASETS, ROOT, load_dataset, synthetic_signal, validate_data
from tslab.metrics import comparison_metrics


class AlgorithmTests(unittest.TestCase):
    def test_original_outputs_match_saved_baseline(self) -> None:
        methods = {
            "MA": alg.moving_average,
            "EMA": alg.exponential_average,
            "SavGol": alg.savitzky_golay,
            "LOESS": alg.local_regression,
            "Gaussian": alg.gaussian_average,
            "Kalman": alg.kalman_filter,
        }
        with np.load(ROOT / "docs/baseline_stage0/curves.npz") as baseline:
            for stem in DATASETS.values():
                values = load_dataset(stem)["value"].to_numpy()
                for name, method in methods.items():
                    with self.subTest(dataset=stem, method=name):
                        actual = method(values)
                        expected = baseline[f"{stem}__{name}"]
                        if name == "MA":
                            # Deliberate change: do not repeat endpoint averages.
                            self.assertTrue(np.isnan(actual[:7]).all())
                            self.assertTrue(np.isnan(actual[-7:]).all())
                            actual, expected = actual[7:-7], expected[7:-7]
                        elif name == "Gaussian" and np.issubdtype(values.dtype, np.integer):
                            # The original SciPy call inherited integer output dtype.
                            # Retain floating-point estimates; document legacy truncation.
                            actual = np.trunc(actual)
                        np.testing.assert_allclose(actual, expected, rtol=1e-10, atol=1e-10)

    def test_gaussian_does_not_truncate_integer_input(self) -> None:
        result = alg.gaussian_average([0, 0, 1, 0, 0])
        self.assertAlmostEqual(result.sum(), 1)
        self.assertTrue(((result > 0) & (result < 1)).all())

    def test_causal_outputs_ignore_future_changes(self) -> None:
        values = np.random.default_rng(3).normal(size=80)
        changed = values.copy()
        changed[40:] += 100
        methods = [
            lambda x: alg.moving_average(x, 5, center=False),
            alg.exponential_average,
            lambda x: alg.exponential_average(x, adjust=False),
            alg.kalman_filter,
        ]
        for method in methods:
            np.testing.assert_allclose(method(values)[:40], method(changed)[:40], equal_nan=True)
        np.testing.assert_allclose(alg.moving_average(np.arange(5), 3, center=False), [np.nan, np.nan, 1, 2, 3])

    def test_savgol_preserves_quadratic(self) -> None:
        x = np.arange(21, dtype=float)
        values = 2 * x**2 + 3 * x + 1
        np.testing.assert_allclose(alg.savitzky_golay(values, 5, 2), values, atol=1e-10)

    def test_invalid_parameters_and_inputs(self) -> None:
        cases = [
            lambda: alg.savitzky_golay(np.ones(5), 5, 5),
            lambda: alg.savitzky_golay(np.ones(50), 51, 2),
            lambda: alg.moving_average(np.ones(3), 5),
            lambda: alg.local_regression(np.ones(3), 0.05),
            lambda: alg.exponential_average([1, np.nan]),
            lambda: alg.exponential_average([1], alpha=0),
            lambda: alg.gaussian_average([], sigma=1),
            lambda: alg.kalman_filter([1], observation_variance=0),
        ]
        for index, run in enumerate(cases):
            with self.subTest(case=index), self.assertRaises(ValueError):
                run()


class DataAndMetricTests(unittest.TestCase):
    def test_synthetic_truth_and_seed(self) -> None:
        first = synthetic_signal("正弦信号", samples=20, dt=0.5, seed=42)
        pd.testing.assert_frame_equal(first, synthetic_signal("正弦信号", samples=20, dt=0.5, seed=42))
        np.testing.assert_allclose(first["truth"], np.sin(2 * np.pi * first.index / 5))
        self.assertEqual(validate_data(first), 0.5)
        constant = synthetic_signal("恒定读数", noise=0)
        np.testing.assert_array_equal(constant["value"], constant["truth"])

    def test_paths_and_time_validation(self) -> None:
        previous = os.getcwd()
        try:
            os.chdir(tempfile.gettempdir())
            self.assertEqual(len(load_dataset("sunspots")), 600)
        finally:
            os.chdir(previous)
        for index in ([0, 0, 1], [2, 1, 0], [0, 1, 3]):
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate_data(pd.DataFrame({"value": [1, 2, 3]}, index=index))

    def test_errors_use_common_points(self) -> None:
        observed = np.arange(4, dtype=float)
        result = comparison_metrics(observed, {"test": np.array([np.nan, 1, 2, 5])}, observed)
        self.assertEqual(result.loc["原始观测", "有效点数"], 3)
        self.assertAlmostEqual(result.loc["test", "RMSE"], np.sqrt(4 / 3))
        self.assertAlmostEqual(result.loc["test", "RPR"], 2)
        self.assertNotIn("RMSE", comparison_metrics(observed, {}).columns)

    def test_constant_empty_and_disconnected_intervals(self) -> None:
        result = comparison_metrics(np.ones(3), {"test": np.ones(3)}, np.ones(3))
        self.assertTrue(result["RPR"].isna().all())
        self.assertTrue((result["RMSE"] == 0).all())
        empty = comparison_metrics(np.ones(3), {"test": np.full(3, np.nan)}, np.ones(3))
        self.assertTrue((empty["有效点数"] == 0).all())
        self.assertTrue(empty["RMSE"].isna().all())
        gaps = comparison_metrics(np.arange(5), {"test": np.array([0, np.nan, 3, np.nan, 8])})
        self.assertTrue(gaps["RPR"].isna().all())


if __name__ == "__main__":
    unittest.main()
