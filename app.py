import streamlit as st
import json
import time
from pathlib import Path
from datetime import date, datetime
import os
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

from src.penalties import (
    get_duration_factor,
    get_activity_factor,
    get_time_penalty,
)
from src.exposure import compute_exposure_score
from src.windows import generate_time_windows
from src.ranker import label_windows



# Page config

st.set_page_config(
    page_title="When Should I Go Out?",
    layout="centered",
)

# Header

st.markdown("## 🏙️ When should I go outside today?")
st.caption(
    "A decision assistant that weighs air quality, duration, "
    "activity, and time-of-day risk."
)

st.markdown("---")

# User inputs

st.markdown("### Tell me about your plan")

col1, col2 = st.columns(2)

with col1:
    duration = st.radio(
        "How long do you plan to stay outside?",
        options=[15, 30, 45, 60],
        index=1,
        format_func=lambda x: f"{x} minutes",
    )

with col2:
    activity = st.selectbox(
        "What will you be doing?",
        options=[
            "standing/errands",
            "walking",
            "brisk walk",
            "running",
        ],
        index=1,
    )

st.caption(
    "Longer duration and higher activity increase pollution exposure."
)

# Analyze button (GATE)

analyze = st.button("Analyze safest time")


# Load AQI data (read-only)


JSON_PATH = Path("data/delhi_hourly_aqi.json")

if not JSON_PATH.exists():
    st.error("AQI data not found. Please run the daily fetch job first.")
    st.stop()

with open(JSON_PATH, "r") as f:
    hourly_aqi = json.load(f)["data"]

today = date.today().strftime("%Y-%m-%d")
hourly_aqi = [h for h in hourly_aqi if h.get("date") == today]

if not hourly_aqi:
    st.error("No AQI data available for today.")
    st.stop()

# COMPUTATION HAPPENS ONLY AFTER BUTTON CLICK

if analyze:
    with st.spinner("Analyzing air quality…"):
        time.sleep(0.5)


        # Compute factors

        duration_factor = get_duration_factor(duration)
        activity_factor = get_activity_factor(activity)

        # Generate windows

        windows = generate_time_windows(hourly_aqi, duration)

        if not windows:
            st.error("No valid time windows found for today.")
            st.stop()


        # Compute exposure

        for w in windows:
            hour_penalties = [get_time_penalty(h) for h in w["hours"]]
            time_penalty = sum(hour_penalties) / len(hour_penalties)

            w["exposure"] = compute_exposure_score(
                w["avg_aqi"],
                duration_factor,
                activity_factor,
                time_penalty,
            )

        # Normalize exposure

        max_exposure = max(w["exposure"] for w in windows)

        for w in windows:
            w["NormalizedScore"] = round(
                (w["exposure"] / max_exposure) * 100, 1
            )

        # Filter future-only windows
       
        current_hour = datetime.now(IST).hour

        windows = [
            w for w in windows
            if w["start_hour"] >= current_hour
        ]

        if not windows:
            st.warning(
                "⚠️ No safe outdoor windows remain today.\n\n"
                "Pollution levels stay high for the rest of the day. "
                "Consider postponing outdoor activity to tomorrow morning."
            )
            st.stop()

        # Rank & label
        windows = sorted(windows, key=lambda x: x["exposure"])
        windows = label_windows(windows)

        best = windows[0]
        worst = windows[-1]
        is_last_window = len(windows) == 1
        risk_multiplier = round(
            worst["exposure"] / best["exposure"], 1
        )

    # RESULTS

    st.markdown("---")
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
        """
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

    st.caption(
    f"Estimated exposure: {round(best['exposure'], 1)} units · "
    "Higher duration or activity increases this value."
    )

    st.markdown("**Why this window:**")
    st.markdown(
        "- Lower pollution compared to other remaining hours\n"
        "- Time-of-day conditions are relatively favorable"
    )

    if is_last_window:
        st.info(
            "This is the only remaining outdoor window today. "
            "If you need to step out, this is the least risky option left."
        )

    st.markdown("---")
    st.markdown("### ❌ Time to avoid")

    st.markdown(
        f"""
        <div style="font-size:28px; font-weight:600; margin-top:8px;">
        🕒 {worst['start_hour']}:00 – {worst['end_hour']}:00
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <span style="
            display:inline-block;
            padding:4px 10px;
            border-radius:999px;
            background:#ff0000;
            color:#ff700;
            font-weight:500;
            margin-top:6px;">
        Highest remaining risk today
        </span>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"**Relative exposure:** {worst['NormalizedScore']} / 100"
    )

    st.caption(
    f"Estimated exposure: {round(worst['exposure'], 1)} units · "
    "Higher duration or activity increases this value."
    )

    st.markdown("**Why to avoid:**")
    st.markdown(
        "- Higher average pollution levels\n"
        "- Time-of-day exposure risk is significantly higher"
    )

    st.markdown("---")
    st.markdown("### ⚠️ Practical advice")

    if not is_last_window:
        st.markdown(
            f"Risk later today is **~{risk_multiplier}× higher** "
            f"than the best window."
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

    
    # Show all windows along with risks

    with st.expander("Show all remaining windows"):
        for w in windows:
            st.write(
                f"{w['start_hour']}:00–{w['end_hour']}:00 · "
                f"Score {w['NormalizedScore']}  "
                f"Exposure {w['exposure']} · {w['label']} . "
            )

