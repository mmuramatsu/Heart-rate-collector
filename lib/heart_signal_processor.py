import numpy as np
import pandas as pd


def clean_rr_intervals(rr_intervals: list[float], high_rr: int = 2000, low_rr: int = 300, interpolation_method_for_outliers: str = "linear", interpolation_method_for_ectopics_beats: str = "linear", ectopic_beats_removal_method: str = "kamath", verbose: bool = True):
    """Clean RR intervals by removing outliers and ectopic beats.

    This function serves as a pipeline to clean RR interval data. It first removes outliers based on physiological limits,
    then removes ectopic beats using a specified method.

    Args:
        rr_intervals (list[float]): A list of RR intervals in milliseconds.
        high_rr (int, optional): The upper limit for a valid RR interval in milliseconds. Values above this will be considered outliers. Defaults to 2000.
        low_rr (int, optional): The lower limit for a valid RR interval in milliseconds. Values below this will be considered outliers. Defaults to 300.
        interpolation_method_for_outliers (str, optional): The method to use for interpolating the outlier values. See pandas.Series.interpolate for options. Defaults to "linear".
        interpolation_method_for_ectopics_beats (str, optional): The method to use for interpolating the ectopic beat values. See pandas.Series.interpolate for options. Defaults to "linear".
        ectopic_beats_removal_method (str, optional): The method to use for removing ectopic beats. Currently, only "kamath" is supported. Defaults to "kamath".
        verbose (bool, optional): If True, prints information about the cleaning process. Defaults to True.

    Returns:
        list[float]: A list of cleaned NN intervals (normal-to-normal intervals).
    """

    cleaned_rr = outliers_removal(
        rr_intervals, high_rr, low_rr, interpolation_method_for_outliers, verbose)
    nn_interval = ectopic_beats_removal(
        cleaned_rr, ectopic_beats_removal_method, interpolation_method_for_ectopics_beats, verbose)

    return nn_interval


def outliers_removal(rr_intervals: list[float], high_rr: int = 2000, low_rr: int = 300, interpolation_method_for_outliers: str = "linear", verbose: bool = True):
    """Remove outliers from a list of RR intervals.

    This function identifies and removes outliers from a list of RR intervals based on upper and lower bounds.
    The removed outliers are then replaced by interpolated values.

    Args:
        rr_intervals (list[float]): A list of RR intervals in milliseconds.
        high_rr (int, optional): The upper limit for a valid RR interval in milliseconds. Values above this will be considered outliers. Defaults to 2000.
        low_rr (int, optional): The lower limit for a valid RR interval in milliseconds. Values below this will be considered outliers. Defaults to 300.
        interpolation_method_for_outliers (str, optional): The method to use for interpolating the outlier values. See pandas.Series.interpolate for options. Defaults to "linear".
        verbose (bool, optional): If True, prints information about the found outliers. Defaults to True.

    Returns:
        list[float]: A list of RR intervals with outliers removed and interpolated.
    """

    cleaned_list = [rr if low_rr <= rr <=
                    high_rr else np.nan for rr in rr_intervals]

    outliers_list = [i for i, value in enumerate(
        cleaned_list) if value == np.nan]

    if verbose:
        print(f"{len(outliers_list)} outliers were found.")
        print(f"The values of the outliers are as follows: {outliers_list}")

    interpoleted_list = interpolate(
        cleaned_list, interpolation_method_for_outliers)

    return interpoleted_list


def ectopic_beats_removal(rr_interval: list[float], method: str = "kamath", interpolation_method_for_ectopics_beats: str = "linear", verbose: bool = True):
    """Remove ectopic beats from a list of RR intervals.

    This function identifies and removes ectopic beats from a list of RR intervals using a specified rule.
    The removed ectopic beats are then replaced by interpolated values.

    Args:
        rr_interval (list[float]): A list of RR intervals in milliseconds.
        method (str, optional): The method to use for ectopic beat detection. Currently, only "kamath" is supported. Defaults to "kamath".
        verbose (bool, optional): If True, prints information about the found ectopic beats. Defaults to True.

    Returns:
        list[float]: A list of NN intervals (normal-to-normal intervals) with ectopic beats removed and interpolated.
    """

    methods_dict = {"kamath": _kamath_rule,
                    }

    rule = methods_dict[method]
    nn_intervals = [rr_interval[0]]
    removed = []
    prev_removed = False

    for i in range(1, len(rr_interval)):
        if rule(rr_interval[i-1], rr_interval[i]) or prev_removed:
            nn_intervals.append(rr_interval[i])
            prev_removed = False
        else:
            nn_intervals.append(np.nan)
            removed.append(rr_interval[i])
            prev_removed = True

    if verbose:
        print(f"{len(removed)} ectopics beats were found.")
        print(f"The values of the outliers are as follows: {removed}")

    interpoleted_list = interpolate(
        nn_intervals, interpolation_method_for_ectopics_beats)

    return interpoleted_list


def _kamath_rule(prev_rr: float, curr_rr: float):
    """Implementation of the Kamath rule for ectopic beat detection.

    This rule checks if the current RR interval is within a certain percentage of the previous RR interval.
    Specifically, it returns False (indicating an ectopic beat) if the current RR is more than 132.5% or less than 75.5% of the previous RR.

    Args:
        prev_rr (float): The previous RR interval in milliseconds.
        curr_rr (float): The current RR interval in milliseconds.

    Returns:
        bool: True if the beat is considered normal, False if it is considered ectopic.
    """

    if curr_rr > prev_rr * 1.325 or curr_rr < prev_rr * 0.755:
        return False

    return True


def interpolate(cleaned_signal: list[float], method: str = "linear"):
    """Interpolate NaN values in a list.

    This function uses pandas to interpolate missing values (represented as NaN) in a list of numbers.

    Args:
        cleaned_signal (list[float]): A list of numbers that may contain NaN values.
        method (str, optional): The interpolation method to use. See pandas.Series.interpolate for options. Defaults to "linear".

    Returns:
        list[float]: A list with NaN values interpolated.
    """

    data_series = pd.Series(cleaned_signal)
    data_series = data_series.interpolate(method=method)
    data_series = data_series.bfill()
    data_series = data_series.ffill()
    return data_series.tolist()
