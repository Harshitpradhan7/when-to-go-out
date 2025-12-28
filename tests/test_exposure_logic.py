import sys
sys.path.append(".")


from src.penalties import get_duration_factor

def test_duration_factor_boundaries():
    assert get_duration_factor(15) == 0.5
    assert get_duration_factor(16) == 1.0
    assert get_duration_factor(30) == 1.0
    assert get_duration_factor(31) == 1.5
    assert get_duration_factor(45) == 1.5
    assert get_duration_factor(46) == 2.0
    assert get_duration_factor(60) == 2.0
    assert get_duration_factor(61) == 3.0


import pytest
from src.penalties import get_activity_factor

def test_valid_activity():
    assert get_activity_factor("walking") == 1.0
    assert get_activity_factor("running") == 1.8

def test_invalid_activity_raises():
    with pytest.raises(KeyError):
        get_activity_factor("cycling")

from src.penalties import get_time_penalty

def test_time_penalty_edges():
    assert get_time_penalty(5.5) == 0.7
    assert get_time_penalty(7.49) == 0.7
    assert get_time_penalty(7.5) == 1.0
    assert get_time_penalty(10.0) == 1.2
    assert get_time_penalty(17.0) == 1.5
    assert get_time_penalty(21.0) == 1.3


from src.windows import generate_time_windows

def test_single_hour_duration():
    hourly = [
        {"hour": 6, "aqi": 100},
        {"hour": 7, "aqi": 200},
    ]

    windows = generate_time_windows(hourly, duration_minutes=30)

    assert len(windows) == 2
    assert windows[0]["avg_aqi"] == 100
    assert windows[1]["avg_aqi"] == 200


def test_multi_hour_window_avg():
    hourly = [
        {"hour": 6, "aqi": 100},
        {"hour": 7, "aqi": 200},
        {"hour": 8, "aqi": 300},
    ]

    windows = generate_time_windows(hourly, duration_minutes=90)

    assert len(windows) == 2
    assert windows[0]["avg_aqi"] == 150  # (100+200)/2
    assert windows[1]["avg_aqi"] == 250  # (200+300)/2


def test_duration_longer_than_data():
    hourly = [
        {"hour": 6, "aqi": 100},
        {"hour": 7, "aqi": 200},
    ]

    windows = generate_time_windows(hourly, duration_minutes=180)

    assert windows == []


from src.exposure import compute_exposure_score

def test_exposure_score_math():
    score = compute_exposure_score(
        avg_aqi=100,
        duration_factor=1.0,
        activity_factor=1.0,
        time_penalty=1.0,
    )
    assert score == 100


from src.ranker import label_windows

def test_labeling_distribution():
    windows = [
        {"exposure": 10},
        {"exposure": 20},
        {"exposure": 30},
        {"exposure": 40},
        {"exposure": 50},
    ]

    labeled = label_windows(windows)

    labels = [w["label"] for w in labeled]
    assert "Best" in labels
    assert "Acceptable" in labels
    assert "Avoid" in labels
