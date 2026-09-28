"""Timing values are limits of filter response, not arbitrary curve shifts."""
import unittest
import numpy as np
from scipy.signal import butter, group_delay
from streamlit.testing.v1 import AppTest
from tslab.data import ROOT
from tslab.timing import smoothing_timing


class TimingTests(unittest.TestCase):
    def test_butterworth_matches_group_delay(self):
        for order in (1,2,4,8):
            sos=butter(order,1.0,fs=10.0,output='sos')
            expected=sum(group_delay((s[:3],s[3:]),w=[0])[1][0] for s in sos)
            row=smoothing_timing('Butterworth（单向）',0.1,cutoff=1,order=order)
            self.assertAlmostEqual(row['低频等效滞后（帧）'],expected,places=10)
            self.assertAlmostEqual(row['低频等效滞后（秒）'],expected*0.1)

    def test_known_delays_and_undefined_cases(self):
        self.assertEqual(smoothing_timing('EMA',0.1,alpha=0.1)['低频等效滞后（帧）'],9)
        self.assertEqual(smoothing_timing('MA（后向）',0.1,window=5)['低频等效滞后（帧）'],2)
        center=smoothing_timing('SG（固定延迟）',0.1,window=5)
        self.assertEqual((center['未来等待（帧）'],center['低频等效滞后（帧）']),(2,0))
        weights=np.exp(-np.arange(5)**2/2); weights/=weights.sum()
        self.assertAlmostEqual(smoothing_timing('Gaussian（单边）',0.1,window=5,sigma=1)['低频等效滞后（帧）'],weights@np.arange(5))
        self.assertTrue(np.isnan(smoothing_timing('LOWESS',0.1)['低频等效滞后（帧）']))
        self.assertTrue(np.isnan(smoothing_timing('Kalman',0.1,process_variance=0)['低频等效滞后（帧）']))
        self.assertGreater(smoothing_timing('Kalman',0.1)['低频等效滞后（帧）'],0)

    def test_tables_and_translation(self):
        app=AppTest.from_file(ROOT/'app.py',default_timeout=30).run()
        self.assertIn('低频等效滞后（秒）',app.dataframe[1].value.columns)
        app.radio(key='language').set_value('en').run()
        self.assertIn('Low-frequency delay (s)',app.dataframe[1].value.columns)
        app.radio(key='mode').set_value('模拟实时').run()
        self.assertFalse(app.exception)
        self.assertIn('Low-frequency delay (s)',app.dataframe[0].value.columns)
