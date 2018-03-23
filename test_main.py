from main import *


def test_average_calc():
    heart_data = [1, 2, 3]
    assert average_calc(heart_data) == 2


def test_interval_average_calc():
    h_time = ["2018-03-23 17:00:36.372339", "2018-03-23 17:10:36.372339", "2018-03-23 17:20:36.372339"]
    h_data = [50, 60, 70]
    interval_start = ["2018-03-23 17:05:36.372339"]
    assert interval_average_calc(h_time, h_data, interval_start) == 65




