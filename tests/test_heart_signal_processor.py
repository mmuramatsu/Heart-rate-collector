import unittest
import numpy as np
from lib.heart_signal_processor import interpolate, _kamath_rule, outliers_removal, ectopic_beats_removal, clean_rr_intervals

class TestHeartSignalProcessor(unittest.TestCase):

    def test_interpolate(self):
        """
        Test the interpolate function.
        """
        signal = [1, 2, np.nan, 4, 5]
        result = interpolate(signal)
        self.assertEqual(result, [1.0, 2.0, 3.0, 4.0, 5.0], "Interpolation of a single NaN value failed.")

        signal = [np.nan, 2, 3, 4, np.nan]
        result = interpolate(signal)
        self.assertEqual(result, [2.0, 2.0, 3.0, 4.0, 4.0], "Interpolation of leading/trailing NaN values failed.")

        signal = [1, 2, np.nan, np.nan, 5]
        result = interpolate(signal)
        self.assertEqual(result, [1.0, 2.0, 3.0, 4.0, 5.0], "Interpolation of multiple consecutive NaN values failed.")

    def test_kamath_rule(self):
        """
        Test the _kamath_rule function.
        """
        # Test case where the beat should be considered normal
        self.assertTrue(_kamath_rule(800, 850), "Normal beat was incorrectly identified as ectopic.")

        # Test case where the beat should be considered ectopic (too high)
        self.assertFalse(_kamath_rule(800, 1100), "Ectopic beat (high) was incorrectly identified as normal.")

        # Test case where the beat should be considered ectopic (too low)
        self.assertFalse(_kamath_rule(800, 500), "Ectopic beat (low) was incorrectly identified as normal.")

    def test_outliers_removal(self):
        """
        Test the outliers_removal function.
        """
        rr_intervals = [800, 820, 250, 810, 2100, 830]
        # With verbose=False to avoid printing during tests
        cleaned_rr = outliers_removal(rr_intervals, high_rr=2000, low_rr=300, verbose=False)
        # The values 250 and 2100 should be identified as outliers and interpolated.
        # Expected: [800, 820, 815, 810, 820, 830] (linear interpolation)
        self.assertAlmostEqual(cleaned_rr[2], 815, delta=1, msg="Outlier (low) was not correctly identified and interpolated.")
        self.assertAlmostEqual(cleaned_rr[4], 820, delta=1, msg="Outlier (high) was not correctly identified and interpolated.")

    def test_ectopic_beats_removal(self):
        """
        Test the ectopic_beats_removal function.
        """
        rr_intervals = [800, 1100, 820, 500, 830]
        # With verbose=False to avoid printing during tests
        nn_intervals = ectopic_beats_removal(rr_intervals, method="kamath", verbose=False)
        # The values 1100 and 500 should be identified as ectopic beats and interpolated.
        # Expected: [800.0, 810.0, 820.0, 825.0, 830.0] (linear interpolation)
        self.assertAlmostEqual(nn_intervals[1], 810, delta=1, msg="Ectopic beat (high) was not correctly identified and interpolated.")
        self.assertAlmostEqual(nn_intervals[3], 825, delta=1, msg="Ectopic beat (low) was not correctly identified and interpolated.")

    def test_clean_rr_intervals(self):
        """
        Test the clean_rr_intervals function.
        """
        rr_intervals = [800, 250, 820, 1100, 830, 2100]
        # With verbose=False to avoid printing during tests
        cleaned_rr = clean_rr_intervals(rr_intervals, high_rr=2000, low_rr=300, verbose=False)
        # This should first remove outliers (250, 2100) and then ectopic beats (1100).
        # The final list should have all these values interpolated.
        # We are not checking the exact interpolated values here, but that the length is the same
        # and that there are no NaNs. A more robust test would check the values more closely.
        self.assertEqual(len(cleaned_rr), len(rr_intervals), "The length of the cleaned RR intervals is incorrect.")
        self.assertFalse(np.isnan(np.sum(cleaned_rr)), "The cleaned RR intervals contain NaN values.")

if __name__ == '__main__':
    unittest.main()
