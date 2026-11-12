import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

st.set_page_config(page_title="Pakistan Airspace Tracker", layout="wide")
st.title("Pakistan Airspace Tracker")


def get_database_url():
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    try:
        return st.secrets["DATABASE_URL"]
    except Exception:
        return None


@st.cache_data(ttl=300)
def load_data():
    engine = create_engine(get_database_url(), pool_pre_ping=True)
    latest = pd.read_sql(
        "SELECT * FROM clean_flights "
        "WHERE fetched_at = (SELECT MAX(fetched_at) FROM clean_flights)",
        engine,
    )
    history = pd.read_sql(
        "SELECT fetched_at, COUNT(*) AS aircraft FROM clean_flights "
        "GROUP BY fetched_at ORDER BY fetched_at",
        engine,
    )
    return latest, history


if not get_database_url():
    st.error("DATABASE_URL not found. Add it to .env (local) or to Streamlit secrets (cloud).")
    st.stop()

latest, history = load_data()

if latest.empty:
    st.info("No data yet. Run the pipeline first.")
    st.stop()

latest_time = latest["fetched_at"].iloc[0]
st.caption(f"Last update (UTC): {latest_time}")

col1, col2, col3 = st.columns(3)
col1.metric("Total aircraft", len(latest))
col2.metric("In the air", int((latest["status"] == "air").sum()))
col3.metric("On the ground", int((latest["status"] == "ground").sum()))

st.subheader("Live map")
st.map(latest[["latitude", "longitude"]])

st.subheader("Aircraft count over time (UTC)")
history["fetched_at"] = pd.to_datetime(history["fetched_at"])
history = history.set_index("fetched_at")
st.line_chart(history["aircraft"])

st.subheader("Aircraft list")
st.dataframe(latest[["callsign", "origin_country", "altitude_ft", "speed_kmh", "status"]])