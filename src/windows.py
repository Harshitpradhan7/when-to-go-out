import math

def generate_time_windows(hourly_aqi: list, duration_minutes: int):
    hours_needed = math.ceil(duration_minutes / 60)
    windows = []

    hourly_aqi = sorted(hourly_aqi, key=lambda x: x["hour"])

    for i in range(len(hourly_aqi) - hours_needed + 1):
        window = hourly_aqi[i : i + hours_needed]

        # ✅ Guard 1: consecutive hours
        hours = [h["hour"] for h in window]
        if hours != list(range(hours[0], hours[0] + hours_needed)):
            continue

        # ✅ Guard 2: valid AQI values
        if any(
            h.get("aqi") is None or h["aqi"] < 0
            for h in window
        ):
            continue

        avg_aqi = sum(h["aqi"] for h in window) / hours_needed
        mid_hour = sum(hours) / hours_needed

        windows.append({
            "start_hour": window[0]["hour"],
            "end_hour": window[-1]["hour"] + 1,
            "avg_aqi": avg_aqi,
            "hours": hours,
        })

    return windows



# import math

# def generate_time_windows(hourly_aqi: list, duration_minutes: int):
#     hours_needed = math.ceil(duration_minutes / 60)
#     windows = []

#     # Ensure sorted by hour
#     hourly_aqi = sorted(hourly_aqi, key=lambda x: x["hour"])

#     for i in range(len(hourly_aqi) - hours_needed + 1):
#         window = hourly_aqi[i : i + hours_needed]

#         # ✅ Guard: hours must be consecutive
#         hours = [h["hour"] for h in window]
#         if hours != list(range(hours[0], hours[0] + hours_needed)):
#             continue

#         avg_aqi = sum(h["aqi"] for h in window) / hours_needed
#         mid_hour = sum(hours) / hours_needed

#         windows.append({
#             "start_hour": window[0]["hour"],
#             "end_hour": window[-1]["hour"] + 1,
#             "avg_aqi": avg_aqi,
#             "mid_hour": mid_hour,
#         })

#     return windows






# import math

# def generate_time_windows(hourly_aqi: list, duration_minutes: int):
#     hours_needed = math.ceil(duration_minutes / 60)
#     windows = []

#     for i in range(len(hourly_aqi) - hours_needed + 1):
#         window = hourly_aqi[i : i + hours_needed]

#         avg_aqi = sum(h["aqi"] for h in window) / hours_needed
#         mid_hour = sum(h["hour"] for h in window) / hours_needed

#         windows.append({
#             "start_hour": window[0]["hour"],
#             "end_hour": window[-1]["hour"] + 1,
#             "avg_aqi": avg_aqi,
#             "mid_hour": mid_hour,
#         })

#     return windows
