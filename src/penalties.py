def get_duration_factor(minutes: int) -> float:
    if minutes <= 15:
        return 0.5
    elif minutes <= 30:
        return 1.0
    elif minutes <= 45:
        return 1.5
    elif minutes <= 60:
        return 2.0
    else:
        return 3.0


def get_activity_factor(activity: str) -> float:
    activity_map = {
        "errands": 0.8,
        "standing": 0.8,
        "walking": 1.0,
        "brisk walk": 1.3,
        "running": 1.8,
        "workout": 1.8,
    }
    return activity_map[activity]


def get_time_penalty(hour: float) -> float:
    if 5.5 <= hour < 7.5:
        return 0.7
    elif 7.5 <= hour < 10:
        return 1.0
    elif 10 <= hour < 17:
        return 1.2
    elif 17 <= hour < 21:
        return 1.5
    else:
        return 1.3
