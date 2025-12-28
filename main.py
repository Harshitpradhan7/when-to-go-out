import json
from pathlib import Path
from datetime import date

from src.penalties import (
    get_duration_factor,
    get_activity_factor,
    get_time_penalty,
)
from src.exposure import compute_exposure_score
from src.windows import generate_time_windows
from src.ranker import label_windows


JSON_PATH = Path("data/delhi_hourly_aqi.json")


with open(JSON_PATH, "r") as f:
    hourly_aqi = json.load(f)["data"]

today = date.today().strftime("%Y-%m-%d")

hourly_aqi = [
    h for h in hourly_aqi
    if h.get("date") == today
]

if not hourly_aqi:
    raise ValueError("No AQI data available for today.")


# User input
duration = 30  # minutes
activity = "walking"

duration_factor = get_duration_factor(duration)
activity_factor = get_activity_factor(activity)

windows = generate_time_windows(hourly_aqi, duration)



for w in windows:
    hour_penalties = [get_time_penalty(h) for h in w["hours"]]
    time_penalty = sum(hour_penalties) / len(hour_penalties)
    w["exposure"] = compute_exposure_score(
        w["avg_aqi"],
        duration_factor,
        activity_factor,
        time_penalty,
    )

    # w["NormalizedScore"] = min(100, w["exposure"] / 10)

max_exposure = max(w["exposure"] for w in windows)

for w in windows:
    w["NormalizedScore"] = round(
        (w["exposure"] / max_exposure) * 100, 1
    )

current_hour = datetime.now().hour -1

windows = [
    w for w in windows
    if w["start_hour"] >= current_hour
]

windows = sorted(windows, key=lambda x: x["exposure"])
windows = label_windows(windows)

# Show top results
for w in windows[:3]:
    print(
        f"{w['start_hour']}:00–{w['end_hour']}:00 | "
        f"AQI {round(w['avg_aqi'])} | "
        f"Score {round(w['NormalizedScore'],1)} | "
        f"{w['label']}"
    )
