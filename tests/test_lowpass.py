"""Butterworth attenuation, initialization, causality and controls."""
import unittest
import numpy as np
from scipy.signal import butter, sosfreqz
from streamlit.testing.v1 import AppTest
from tslab.algorithms import butterworth_lowpass
from tslab.data import ROOT
from tslab.realtime import replay_signal


class LowpassTests(unittest.TestCase):
    def test_frequency_response_and_filter_attenuation(self):
        dt, cutoff = 0.01, 5.0
        sos = butter(2, cutoff, fs=1/dt, output='sos')
        _, response = sosfreqz(sos, worN=[cutoff], fs=1/dt)
        self.assertAlmostEqual(abs(response[0]), 1/np.sqrt(2), places=10)
        time = np.arange(4000)*dt
        for freq in (1.0, 20.0):
            values = np.sin(2*np.pi*freq*time)
            for zero_phase in (False, True):
                result = butterworth_lowpass(values, dt, cutoff, zero_phase=zero_phase)
                expected = abs(sosfreqz(sos, worN=[freq], fs=1/dt)[1][0])**(2 if zero_phase else 1)
                measured = np.sqrt(np.mean(result[1000:-1000]**2)*2)
                self.assertAlmostEqual(measured, expected, places=5)

    def test_prefix_stability_constant_and_invalid_inputs(self):
        values = np.random.default_rng(3).normal(size=60)
        full = butterworth_lowpass(values, 0.1, 1.0)
        for count in (1, 2, 15, 40):
            replay, delay, startup = replay_signal(values[:count], 'Butterworth（单向）', dt=0.1, cutoff=1.0)
            np.testing.assert_allclose(replay, full[:count])
            self.assertEqual((delay,startup), (0,1))
        for zero_phase in (False,True):
            np.testing.assert_allclose(butterworth_lowpass(np.ones(100), 0.1, 1, zero_phase=zero_phase), 1, atol=1e-12)
        for dt, cutoff, order in [(0,1,2),(0.1,5,2),(0.1,0,2),(0.1,1,0),(0.1,1,2.5)]:
            with self.assertRaises(ValueError): butterworth_lowpass(values,dt,cutoff,order)
        with self.assertRaises(ValueError): butterworth_lowpass([1,2,3],0.1,1,zero_phase=True)

    def test_offline_replay_language_short_data_and_dt(self):
        app=AppTest.from_file(ROOT/'app.py', default_timeout=30).run()
        app.multiselect(key='methods_causal').set_value(['Butterworth（单向）'])
        app.multiselect(key='methods_offline').set_value(['Butterworth（双向）']).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.number_input(key='lp_cutoff').value,1.0)
        before=app.dataframe[0].value.to_numpy()
        app.radio(key='language').set_value('en').run()
        np.testing.assert_array_equal(before,app.dataframe[0].value.to_numpy())
        app.number_input(key='dt').set_value(10.0).run()
        self.assertLess(app.number_input(key='lp_cutoff').value,0.05)
        app.number_input(key='samples').set_value(3).run()
        self.assertFalse(app.exception)
        self.assertTrue(any('Not enough samples' in w.value for w in app.warning))
        app.radio(key='mode').set_value('模拟实时').run()
        app.multiselect(key='rt_causal').set_value(['Butterworth（单向）'])
        app.multiselect(key='rt_delayed').set_value([]).run()
        app.button(key='rt_step').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.slider(key='rt_count').value,2)
        app.slider(key='rt_lp_order').set_value(3).run()
        self.assertEqual(app.slider(key='rt_count').value,1)
        self.assertNotIn('Butterworth (forward-backward)',app.multiselect(key='rt_delayed').options)
