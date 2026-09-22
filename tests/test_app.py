"""Application-level checks for selection, parameter constraints and metrics."""

import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from tslab.data import ROOT
from tslab.plotting import METHOD_COLORS


class ApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        self.assertFalse(self.app.exception)

    def test_unselected_methods_are_not_executed(self) -> None:
        with patch("tslab.algorithms.savitzky_golay", side_effect=AssertionError("Unselected method executed")):
            self.app.run()
            self.assertFalse(self.app.exception)
        self.assertIn("RMSE", self.app.dataframe[0].value.columns)
        self.app.multiselect[0].set_value([]).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.dataframe), 0)
        self.assertEqual(len(self.app.get("plotly_chart")), 1)

    def test_all_bundled_datasets_without_truth(self) -> None:
        self.app.selectbox(key="source").select("内置数据集").run()
        self.app.multiselect(key="methods_causal").set_value(["MA（后向）", "EMA", "Kalman"])
        self.app.multiselect(key="methods_offline").set_value(["MA（居中）", "SavGol", "LOWESS", "Gaussian"]).run()
        for label in self.app.selectbox(key="dataset").options:
            with self.subTest(dataset=label):
                self.app.selectbox(key="dataset").select(label).run()
                self.assertFalse(self.app.exception)
                self.assertFalse(self.app.warning)
                table = self.app.dataframe[0].value
                self.assertNotIn("RMSE", table.columns)
                self.assertEqual(len(table), 8)

    def test_savgol_constraints_follow_window_and_data_size(self) -> None:
        self.app.multiselect(key="methods_causal").set_value([])
        self.app.multiselect(key="methods_offline").set_value(["SavGol"]).run()
        self.app.select_slider(key="sg_degree").set_value(5).run()
        self.app.select_slider(key="sg_window").set_value(5).run()
        self.assertLess(self.app.select_slider(key="sg_degree").value, 5)
        self.app.select_slider(key="sg_window").set_value(51).run()
        self.app.number_input(key="samples").set_value(50).run()
        self.assertLessEqual(self.app.select_slider(key="sg_window").value, 50)
        self.assertFalse(self.app.exception)
        self.app.number_input(key="samples").set_value(3).run()
        self.app.multiselect(key="methods_causal").set_value(["MA（后向）", "EMA", "Kalman"])
        self.app.multiselect(key="methods_offline").set_value(["MA（居中）", "SavGol", "LOWESS", "Gaussian"]).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.dataframe[0].value["有效点数"].iloc[0], 0)
        self.assertTrue(any("没有共同有效点" in w.value for w in self.app.warning))

    def test_causal_mode_and_constant_signal(self) -> None:
        self.assertEqual(self.app.multiselect[0].options, ["MA（后向）", "EMA", "Kalman"])
        self.app.multiselect[0].set_value(self.app.multiselect[0].options).run()
        self.app.selectbox(key="scenario").select("恒定读数").run()
        self.app.slider(key="noise").set_value(0.0).run()
        self.assertFalse(self.app.exception)
        table = self.app.dataframe[0].value
        self.assertTrue(table["RPR"].isna().all())
        self.assertTrue((table["RMSE"] == 0).all())
        self.app.radio(key="mode").set_value("离线对比").run()
        self.assertFalse(self.app.exception)

    def test_empty_lowess_parameter_has_readable_validation(self) -> None:
        self.app.multiselect(key="methods_causal").set_value([])
        self.app.multiselect(key="methods_offline").set_value(["LOWESS"]).run()
        self.app.run()
        self.app.number_input(key="lowess_fraction").set_value(None).run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("请输入邻域比例" in w.value for w in self.app.warning))


if __name__ == "__main__":
    unittest.main()
