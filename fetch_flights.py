import json
import time
import sqlite3
import requests
import pandas as pd
import shapely
from shapely.geometry import shape
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

with open("pakistan.geo.json", encoding="utf-8") as file:
    PAKISTAN = shape(json.load(file)["geometry"])


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
    raw = pd.read_sql(
        "SELECT * FROM raw_flights WHERE latitude IS NOT NULL AND longitude IS NOT NULL",
        conn,
    )

    inside = shapely.contains_xy(PAKISTAN, raw["longitude"], raw["latitude"])
    raw = raw[inside]

    clean = pd.DataFrame({
        "icao24": raw["icao24"],
        "callsign": raw["callsign"].str.strip(),
        "origin_country": raw["origin_country"],
        "latitude": raw["latitude"],
        "longitude": raw["longitude"],
        "altitude_ft": (raw["baro_altitude"] * 3.28084).round(),
        "speed_kmh": (raw["velocity"] * 3.6).round(1),
        "status": raw["on_ground"].apply(lambda v: "ground" if v == 1 else "air"),
        "fetched_at": raw["fetched_at"],
    })

    clean.to_sql("clean_flights", conn, if_exists="replace", index=False)
    conn.close()
    return len(clean)


while True:
    now = datetime.now().strftime("%H:%M:%S")
    try:
        new_rows = fetch_and_save()
        clean_total = build_clean_table()
        print(f"[{now}] new rows: {new_rows} | clean rows inside Pakistan: {clean_total}")
    except Exception as error:
        print(f"[{now}] error: {error}")
    time.sleep(INTERVAL_SECONDS)