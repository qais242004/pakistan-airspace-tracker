import sqlite3

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
print("clean_flights mein rows:", total)

print("Pehli 5 rows:")
for row in conn.execute("SELECT callsign, origin_country, altitude_ft, speed_kmh, status, fetched_at FROM clean_flights LIMIT 5"):
    print(row)

conn.close()