"""Presentation changes must preserve experiment state and numerical results."""

import ast
import json
import re
import string
import tomllib
import unittest
from unittest.mock import PropertyMock, patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
from streamlit.runtime.context import ContextProxy, StreamlitTheme

from tslab.data import ROOT, synthetic_signal
from tslab.i18n import ENGLISH, translate
from tslab.plotting import DARK_METHOD_COLORS, METHOD_COLORS, error_figure, signal_figure


class LanguageTests(unittest.TestCase):
    def test_switching_language_preserves_experiment(self) -> None:
        app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        app.multiselect[0].set_value(list(METHOD_COLORS)).run()
        app.selectbox(key="scenario").select("缓慢趋势")
        app.number_input(key="samples").set_value(100)
        app.number_input(key="seed").set_value(19)
        app.slider(key="noise").set_value(0.7)
        app.slider(key="ema_alpha").set_value(0.4)
        app.select_slider(key="sg_window").set_value(9)
        app.run()
        before = app.dataframe[0].value
        before_chart = json.loads(app.get("plotly_chart")[0].proto.spec)

        app.radio(key="language").set_value("en").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.number_input(key="samples").value, 100)
        self.assertEqual(app.number_input(key="seed").value, 19)
        self.assertEqual(app.slider(key="ema_alpha").value, 0.4)
        self.assertEqual(app.select_slider(key="sg_window").value, 9)
        self.assertEqual(app.selectbox(key="scenario").value, "缓慢趋势")
        self.assertEqual(app.multiselect[0].value, list(METHOD_COLORS))
        np.testing.assert_array_equal(before.to_numpy(), app.dataframe[0].value.to_numpy())
        self.assertIn("Valid samples", app.dataframe[0].value.columns)
        self.assertEqual(app.dataframe[0].value.index.name, "Method")
        chart = json.loads(app.get("plotly_chart")[0].proto.spec)
        self.assertEqual(chart["layout"]["xaxis"]["title"]["text"], "Time (s)")
        self.assertEqual([d["y"] for d in chart["data"]], [d["y"] for d in before_chart["data"]])
        for element_type in ("title", "caption", "markdown", "subheader", "warning", "info"):
            for element in app.get(element_type):
                self.assertIsNone(re.search(r"[\u4e00-\u9fff]", element.value), element.value)
        app.radio(key="language").set_value("zh").run()
        self.assertFalse(app.exception)
        pd.testing.assert_frame_equal(before, app.dataframe[0].value)

    def test_english_dataset_causal_mode_and_validation(self) -> None:
        app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        app.selectbox(key="source").select("内置数据集").run()
        app.selectbox(key="dataset").select("风速 · Wind Speed").run()
        app.number_input(key="points_long_term_weather_wv").set_value(100).run()
        app.radio(key="mode").set_value("仅因果方法").run()
        app.multiselect[0].set_value(["MA（后向）", "EMA"]).run()
        app.radio(key="language").set_value("en").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.radio(key="mode").value, "仅因果方法")
        self.assertEqual(app.selectbox(key="dataset").value, "风速 · Wind Speed")
        self.assertEqual(app.number_input(key="points_long_term_weather_wv").value, 100)
        self.assertNotIn("RMSE", app.dataframe[0].value.columns)
        self.assertIn("MA (trailing)", app.multiselect[0].options)
        app.radio(key="mode").set_value("离线对比").run()
        app.multiselect[0].set_value(["LOWESS"]).run()
        app.run()
        app.number_input(key="lowess_fraction").set_value(None).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Enter a neighborhood fraction" in w.value for w in app.warning))

    def test_translation_templates_and_error_coverage(self) -> None:
        formatter = string.Formatter()
        for source, target in ENGLISH.items():
            with self.subTest(text=source):
                fields = lambda text: {f for _, f, _, _ in formatter.parse(text) if f is not None}
                self.assertEqual(fields(source), fields(target))
        for path in (ROOT / "tslab/data.py", ROOT / "tslab/algorithms.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                    message = node.exc.args[0]
                    if isinstance(message, ast.Constant) and isinstance(message.value, str):
                        self.assertNotEqual(translate(message.value, "en"), message.value)


class ThemeTests(unittest.TestCase):
    def test_app_theme_change_preserves_parameters_and_metrics(self) -> None:
        app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        app.slider(key="ema_alpha").set_value(0.42).run()
        before = app.dataframe[0].value.copy()
        with patch.object(ContextProxy, "theme", new_callable=PropertyMock) as theme:
            theme.return_value = StreamlitTheme({"type": "dark"})
            app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.slider(key="ema_alpha").value, 0.42)
        pd.testing.assert_frame_equal(before, app.dataframe[0].value)
        chart = json.loads(app.get("plotly_chart")[0].proto.spec)
        self.assertEqual(chart["layout"]["font"]["color"], "#E7EDF5")
        self.assertEqual(chart["data"][1]["line"]["color"], "#F0F3F8")

    def test_chart_styles_and_values_in_both_themes(self) -> None:
        data = synthetic_signal("正弦信号", samples=20)
        truth = data["truth"].to_numpy()
        estimates = {name: truth.copy() for name in METHOD_COLORS}
        figures = []
        for theme in ("light", "dark"):
            figure = signal_figure(data.index, data["value"].to_numpy(), estimates, truth, language="en", theme=theme)
            error = error_figure(data.index, estimates, truth, language="en", theme=theme)
            self.assertEqual(figure.layout.paper_bgcolor, "rgba(0,0,0,0)")
            self.assertEqual(error.layout.font.color, figure.layout.font.color)
            self.assertEqual(error.layout.yaxis.title.text, "Estimate − truth")
            colors = DARK_METHOD_COLORS if theme == "dark" else METHOD_COLORS
            for trace, (name, values) in zip(figure.data[2:], estimates.items()):
                self.assertEqual(trace.line.color, colors[name])
                np.testing.assert_array_equal(trace.y, values)
            figures.append(figure)
        self.assertNotEqual(figures[0].data[1].line.color, figures[1].data[1].line.color)
        self.assertNotEqual(figures[0].layout.font.color, figures[1].layout.font.color)

    def test_native_themes_are_configured(self) -> None:
        config = tomllib.loads((ROOT / ".streamlit/config.toml").read_text())
        light, dark = config["theme"]["light"], config["theme"]["dark"]
        self.assertNotEqual(light["backgroundColor"], dark["backgroundColor"])
        self.assertNotEqual(light["textColor"], dark["textColor"])


if __name__ == "__main__":
    unittest.main()
