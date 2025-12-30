import json
import os
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
JSON_PATH = DATA_DIR / "delhi_hourly_aqi.json"
PARQUET_PATH = DATA_DIR / "delhi_hourly_aqi.parquet"


def fetch_and_store_hourly_city_aqi(
    lat=28.7041,
    lon=77.1025,
):
    # ---------- FETCH ----------
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "us_aqi",
        "forecast_days": 3,
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()["hourly"]
    times = data["time"]
    aqi_values = data["us_aqi"]

    hourly_aqi = []
    for t, aqi in zip(times, aqi_values):
        dt = datetime.fromisoformat(t)
        hourly_aqi.append({
            "date": dt.strftime("%Y-%m-%d"),
            "hour": dt.hour,
            "aqi": int(aqi),
        })

    DATA_DIR.mkdir(exist_ok=True)

    # ---------- JSON (overwrite snapshot) ----------
    with open(JSON_PATH, "w") as f:
        json.dump(
            {
                "fetched_at": datetime.utcnow().isoformat(),
                "data": hourly_aqi,
            },
            f,
            indent=2,
        )

    # ---------- PARQUET (append with dedupe) ----------
    df_new = pd.DataFrame(hourly_aqi)

    if PARQUET_PATH.exists():
        df_old = pd.read_parquet(PARQUET_PATH)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
        df_final = df_final.drop_duplicates(
            subset=["date", "hour"], keep="last"
        )
    else:
        df_final = df_new

    df_final.to_parquet(PARQUET_PATH, index=False)

    return hourly_aqi
