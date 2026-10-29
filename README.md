# Riyadh Fly

**Flight Data Analysis and Forecasting at King Khalid International Airport (RUH)**

Riyadh Fly is a data analysis project that explores flight activity at King Khalid International Airport in Riyadh, Saudi Arabia. The project uses data analysis, machine learning, and an interactive dashboard to understand flight patterns and forecast future activity.

## Project Overview

The project analyzes flight data from **April to September 2025 (Q2 and Q3)** and forecasts flight activity for **October to December 2025 (Q4)**.

### Key Features

- Analyze daily and monthly flight activity.
- Identify the most popular destinations and most active airlines.
- Discover the busiest hours of the day.
- Forecast daily flight counts and hourly activity using Random Forest Regression.
- Display historical data and forecasts in an interactive dashboard.

## Project Structure

```text
Riyadh-Fly/
│
├── riyadh_fly_dashboard/
│   ├── app.py
│   ├── favicon.png
│   ├── riyadh_fly_cleaned.csv
│   ├── requirements.txt
│   └── .streamlit/
│       └── config.toml
│
├── EDA Project.ipynb
├── PDF Report.pdf
└── README.md
```

### Files Description

**Dashboard folder — `riyadh_fly_dashboard/`**

- `app.py` — The main code for the interactive Streamlit dashboard.
- `favicon.png` — The dashboard page icon.
- `riyadh_fly_cleaned.csv` — The cleaned dataset containing 135,456 flight records.
- `requirements.txt` — The Python libraries required to run the dashboard.
- `.streamlit/config.toml` — The configuration file for the dashboard's light theme.

**Other project files**

- `EDA Project.ipynb` — Contains data exploration, cleaning, visualizations, and analysis.
- `PDF Report.pdf` — Presents the project methodology, findings, and conclusions.

## Dataset

The dataset was obtained from Kaggle:

[King Khalid International Airport Flights Dataset](https://www.kaggle.com/datasets/mohammedalsubaie/king-khalid-international-airport-flights-dataset/data)

The cleaned dataset contains **135,456 records** and is used for data analysis, visualizations, and forecasting.

## How to Explore the Dashboard

Explore the interactive Riyadh Fly dashboard online:

[**Open Riyadh Fly Dashboard**](https://riyadh-fly.streamlit.app/)

## Author

**Sulaiman Allumaylim**
