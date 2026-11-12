import os
import json
import requests
import pandas as pd
import shapely
from shapely.geometry import shape
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

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

with open("pakistan.geo.json", encoding="utf-8") as file:
    PAKISTAN = shape(json.load(file)["geometry"])


def fetch_planes():
    response = requests.get(URL, params=PARAMS, timeout=30)
    response.raise_for_status()
    data = response.json()

    planes = data["states"] or []
    df = pd.DataFrame(planes, columns=COLUMNS)
    for col in ["time_position", "last_contact"]:
        df[col] = df[col].astype("float64")
    df["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return df


def clean_planes(raw):
    raw = raw[raw["latitude"].notna() & raw["longitude"].notna()]
    inside = shapely.contains_xy(PAKISTAN, raw["longitude"], raw["latitude"])
    raw = raw[inside]

    return pd.DataFrame({
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


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL nahi mila, .env file check karo")

    engine = create_engine(database_url, pool_pre_ping=True)

    raw = fetch_planes()
    clean = clean_planes(raw)

    raw.to_sql("raw_flights", engine, if_exists="append", index=False)
    clean.to_sql("clean_flights", engine, if_exists="append", index=False)

    with engine.connect() as conn:
        raw_total = conn.execute(text("SELECT COUNT(*) FROM raw_flights")).scalar()
        clean_total = conn.execute(text("SELECT COUNT(*) FROM clean_flights")).scalar()

    print(f"Is run mein: raw {len(raw)} | clean (Pakistan) {len(clean)}")
    print(f"Neon mein total: raw {raw_total} | clean {clean_total}")


main()