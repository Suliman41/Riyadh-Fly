# Riyadh Fly — RUH Flight Records Analytics

Streamlit analytics app for scheduled flight records at King Khalid International Airport (RUH):
historical analysis for **Q2 2025 (Apr–Jun)** and **Q3 2025 (Jul–Sep)**, plus a **Q4 2025 (Oct–Dec) forecast**.

## Run locally
```bash
cd riyadh_fly_dashboard
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Opens at http://localhost:8501.

## Structure
```
riyadh_fly_dashboard/
├── app.py                  # Application
├── favicon.png             # Page icon
├── riyadh_fly_cleaned.csv  # Cleaned dataset (135,456 records)
├── requirements.txt
└── .streamlit/config.toml  # Light theme
```

## Using the app
- **Left panel** — switch between *Dashboard* and *Dataset Description*; flight type, airline and destination filters (apply to Q2 and Q3).
- **Reporting quarter** — Q2 · 2025, Q3 · 2025 (historical) or Q4 · 2025 (forecast).
- **Navigation** — four views per quarter. Historical views end with an analytical question and a data-driven insight; forecast views end with the prediction methodology.

## Q4 forecast data
The Q4 values are static results produced in the project's Jupyter notebook and stored in `app.py`
(`FORECAST_MONTHLY`, `FORECAST_DESTINATIONS`, `FORECAST_AIRLINES`, `FORECAST_HOURS`). They are displayed as supplied, not recalculated.

