import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pakistan Airspace Tracker", layout="wide")
st.title("Pakistan Airspace Tracker")

conn = sqlite3.connect("flights.db")
df = pd.read_sql("SELECT * FROM clean_flights", conn)
conn.close()

latest_time = df["fetched_at"].max()
latest = df[df["fetched_at"] == latest_time]

st.caption(f"Last update (UTC): {latest_time}")

col1, col2, col3 = st.columns(3)
col1.metric("Total aircraft", len(latest))
col2.metric("In the air", int((latest["status"] == "air").sum()))
col3.metric("On the ground", int((latest["status"] == "ground").sum()))

st.subheader("Live map")
st.map(latest[["latitude", "longitude"]])

st.subheader("Aircraft count over time (UTC)")
history = df.groupby("fetched_at").size().reset_index(name="aircraft")
history["fetched_at"] = pd.to_datetime(history["fetched_at"])
history = history.set_index("fetched_at")
st.line_chart(history["aircraft"])

st.subheader("Aircraft list")
st.dataframe(latest[["callsign", "origin_country", "altitude_ft", "speed_kmh", "status"]])