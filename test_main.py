import datetime


def test_average_calc():
    from main import average_calc
    heart_data = [1, 2, 3, 4]
    assert average_calc(heart_data) == 5
