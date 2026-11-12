\# Pakistan Airspace Tracker



A data engineering project that collects live aircraft data over Pakistan every 15 minutes, cleans it, stores the history, and shows it on a live dashboard.



\## Architecture



OpenSky Network API -> Python ingestion script -> SQLite (raw\_flights) -> SQL transform (clean\_flights) -> Streamlit dashboard



\## What each stage does



\- \*\*Ingest:\*\* a Python script calls the OpenSky API every 15 minutes for aircraft inside a bounding box around Pakistan.

\- \*\*Store:\*\* every fetch is appended to a `raw\_flights` table, untouched, so the history is never lost.

\- \*\*Transform:\*\* SQL builds a `clean\_flights` table. It trims callsigns, converts meters to feet and m/s to km/h, labels aircraft as air or ground, and drops rows without a position.

\- \*\*Dashboard:\*\* Streamlit shows the latest aircraft count, a live map, an aircraft count over time chart, and a list of aircraft.



\## Tech stack



Python, pandas, requests, SQLite, SQL, Streamlit



\## How to run



1\. Install packages: `pip install -r requirements.txt`

2\. Start the pipeline (keep it running): `python fetch\_flights.py`

3\. Start the dashboard: `streamlit run dashboard.py`



\## Data source



OpenSky Network API (free for research and non-commercial use).



\## Roadmap



\- Keep only aircraft inside Pakistan's real borders (the bounding box also catches parts of India and Afghanistan)

\- Move storage to a cloud database and run the pipeline on a cloud scheduler

\- Publish the dashboard with a public link

