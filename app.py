import streamlit as st
from datetime import date
import json
from pathlib import Path

import json
from pathlib import Path
from datetime import datetime, date
# from datetime import date


from src.penalties import (
    get_duration_factor,
    get_activity_factor,
    get_time_penalty,
)
from src.exposure import compute_exposure_score
from src.windows import generate_time_windows
from src.ranker import label_windows

# -----------------------
# Page config
# -----------------------
st.set_page_config(
    page_title="When Should I Go Out?",
    layout="centered",
)

# -----------------------
# Load data (read-only)
# -----------------------
JSON_PATH = Path("data/delhi_hourly_aqi.json")

with open(JSON_PATH, "r") as f:
    hourly_aqi = json.load(f)["data"]

today = date.today().strftime("%Y-%m-%d")
hourly_aqi = [h for h in hourly_aqi if h["date"] == today]
#################################

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

current_hour = datetime.now().hour

windows = [
    w for w in windows
    if w["start_hour"] >= current_hour
]

windows = sorted(windows, key=lambda x: x["exposure"])
windows = label_windows(windows)




##################################
# windows = ...
best = windows[0]
worst = windows[-1]
is_last_window = len(windows) == 1
risk_multiplier = round(worst["exposure"] / best["exposure"], 1)

# -----------------------
# Header
# -----------------------
st.markdown("## 🏙️ When should I go outside today?")
st.caption(
    "A decision assistant that weighs air quality, duration, "
    "activity, and time-of-day risk."
)

st.markdown("---")

# -----------------------
# BEST WINDOW (Hero)
# -----------------------
st.markdown("### ✅ Best time to go out (from now)")

st.markdown(
    f"""
<div style="font-size:28px; font-weight:600; margin-top:8px;">
🕒 {best['start_hour']}:00 – {best['end_hour']}:00
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<span style="
    display:inline-block;
    padding:4px 10px;
    border-radius:999px;
    background:#e6f4ea;
    color:#137333;
    font-weight:500;
    margin-top:6px;">
Lowest remaining risk today
</span>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"**Relative exposure:** {best['NormalizedScore']} / 100"
)

st.markdown("**Why this window:**")
st.markdown(
    "- Lower pollution compared to other remaining hours\n"
    "- Reduced traffic-related emissions"
)

if is_last_window:
    st.info(
        "This is the only remaining outdoor window today. "
        "If you need to step out, this is the least risky option left."
    )

st.markdown("---")

# -----------------------
# WORST WINDOW
# -----------------------
st.markdown("### ❌ Time to avoid")

st.markdown(
    f"""
<div style="font-size:20px; font-weight:500;">
🕒 {worst['start_hour']}:00 – {worst['end_hour']}:00
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"**Relative exposure:** {worst['NormalizedScore']} / 100"
)

st.markdown("**Why to avoid:**")
st.markdown(
    "- Higher average AQI during this period\n"
    "- Time-of-day conditions increase exposure"
)

st.markdown("---")

# -----------------------
# Context-aware advice
# -----------------------
st.markdown("### ⚠️ Practical advice")

if not is_last_window:
    st.markdown(
        f"Risk later today is **~{risk_multiplier}× higher** than the best window."
    )

if risk_multiplier >= 2:
    st.warning(
        "Outdoor exposure is strongly discouraged later today. "
        "Postpone if possible."
    )
elif risk_multiplier >= 1.4:
    st.markdown(
        "- Prefer shorter trips\n"
        "- Avoid brisk walking or workouts"
    )
else:
    st.markdown(
        "Risk difference is modest. Short trips are manageable with caution."
    )

# -----------------------
# Optional: Show all windows
# -----------------------
with st.expander("Show all remaining windows"):
    for w in windows:
        st.write(
            f"{w['start_hour']}:00–{w['end_hour']}:00 · "
            f"Score {w['NormalizedScore']} · {w['label']}"
        )
