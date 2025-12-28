def compute_exposure_score(avg_aqi: float, duration_factor: float, activity_factor: float, time_penalty: float) -> float:
    return avg_aqi * duration_factor * activity_factor * time_penalty
