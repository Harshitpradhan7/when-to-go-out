from src.aqi_api import fetch_and_store_hourly_city_aqi
from datetime import datetime
import pytz

# IST = pytz.timezone("Asia/Kolkata")
# now_ist = datetime.now(IST)

# today = now_ist.strftime("%Y-%m-%d")
# current_hour = now_ist.hour

def run():
    fetch_and_store_hourly_city_aqi()

if __name__ == "__main__":
    run()
