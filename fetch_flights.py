import time
import sqlite3
import requests
import pandas as pd
from datetime import datetime, timezone

URL = "https://opensky-network.org/api/states/all"

PARAMS = {
    "lamin": 23.5,
    "lamax": 37.1,
    "lomin": 60.9,
    "lomax": 77.8,
}

COLUMNS = [
    "icao24", "callsign", "origin_country", "time_position", "last_contact",
    "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
    "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
    "spi", "position_source",
]

INTERVAL_SECONDS = 900


def fetch_and_save():
    response = requests.get(URL, params=PARAMS, timeout=30)
    response.raise_for_status()
    data = response.json()

    planes = data["states"] or []
    df = pd.DataFrame(planes, columns=COLUMNS)
    df["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("flights.db")
    df.to_sql("raw_flights", conn, if_exists="append", index=False)
    conn.close()
    return len(df)


def build_clean_table():
    conn = sqlite3.connect("flights.db")
    conn.execute("DROP TABLE IF EXISTS clean_flights")
    conn.execute("""
    CREATE TABLE clean_flights AS
    SELECT
        icao24,
        TRIM(callsign) AS callsign,
        origin_country,
        latitude,
        longitude,
        ROUND(baro_altitude * 3.28084) AS altitude_ft,
        ROUND(velocity * 3.6, 1) AS speed_kmh,
        CASE WHEN on_ground = 1 THEN 'ground' ELSE 'air' END AS status,
        fetched_at
    FROM raw_flights
    WHERE latitude IS NOT NULL
      AND longitude IS NOT NULL
    """)
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM clean_flights").fetchone()[0]
    conn.close()
    return total


while True:
    now = datetime.now().strftime("%H:%M:%S")
    try:
        new_rows = fetch_and_save()
        clean_total = build_clean_table()
        print(f"[{now}] new rows: {new_rows} | clean table total: {clean_total}")
    except Exception as error:
        print(f"[{now}] error: {error}")
    time.sleep(INTERVAL_SECONDS)