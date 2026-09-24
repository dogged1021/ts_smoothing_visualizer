"""Direct Gaussian derivative units, orientation and sampling limitations."""
import unittest
import numpy as np
from streamlit.testing.v1 import AppTest
from tslab.algorithms import gaussian_derivatives, gaussian_average
from tslab.data import ROOT


class GaussianDerivativeTests(unittest.TestCase):
    def test_units_signal_and_derivative_direction(self):
        time = np.arange(501)*0.05
        first = gaussian_derivatives(np.sin(time), 0.05)
        second = gaussian_derivatives(np.sin(time), 0.1)
        np.testing.assert_allclose(first['signal'], gaussian_average(np.sin(time)))
        np.testing.assert_allclose(second['d1'], first['d1']/2)
        np.testing.assert_allclose(second['d2'], first['d2']/4)
        np.testing.assert_allclose(first['d1'][10:-10], np.cos(time[10:-10]), atol=0.01)
        np.testing.assert_allclose(first['d2'][10:-10], -np.sin(time[10:-10]), atol=0.05)
        constant = gaussian_derivatives(np.ones(30), 0.1, sigma=0.5)
        np.testing.assert_allclose(constant['d1'], 0)
        self.assertGreater(np.max(np.abs(constant['d2'])), 1)
        for dt, sigma in [(0,2), (0.1,0), (np.nan,2)]:
            with self.assertRaises(ValueError): gaussian_derivatives([1,2,3], dt, sigma)

    def test_shared_sigma_and_language(self):
        app=AppTest.from_file(ROOT/'app.py', default_timeout=30).run()
        app.radio(key='application').set_value('导数与变化率估计').run()
        app.multiselect(key='d_methods_offline').set_value(['Gaussian 后差分','Gaussian 导数核']).run()
        self.assertFalse(app.exception)
        self.assertEqual(len([x for x in app.slider if x.key=='d_sigma']),1)
        app.slider(key='d_sigma').set_value(1.5).run()
        before=app.dataframe[0].value.iloc[:,2:].to_numpy()
        app.radio(key='language').set_value('en').run()
        self.assertFalse(app.exception)
        np.testing.assert_array_equal(before, app.dataframe[0].value.iloc[:,2:].to_numpy())
