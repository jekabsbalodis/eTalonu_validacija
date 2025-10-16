# 🚋 eTalonu Validācija

This repository powers the Streamlit Community Cloud app that visualizes
**Riga city public‑transport ticket (eTalons) validation data**.

## What the app shows

The dashboard provides interactive visualisations of public transport usage in Riga:

## Key metrics

- **Monthly ridership** - Total rides per month
- **Daily averages** - Average rides per day
- **Peak activity hour** - Most active hour of the day

## Charts

- **Rides per day of week** - Average rides per day for each day of week
- **Transport type distribution** - How rides are distributed across buses, trams and troleybuses
- **Popular routes** - Top 15 routes ranked by count of rides
- **Route intensity** - Average rides per vehicle for the top 15 routes

## Filters

- Select any month from the available range
- Filter by transport type (Bus, Tram, Trolleybus)

## Data source

The validation records are pulled from **Latvia’s Open Data portal**:

- Dataset: _e‑talonu validāciju dati Rīgas satiksme sabiedriskajos transportlīdzekļos_
- URL: <https://data.gov.lv/dati/eng/dataset/e-talonu-validaciju-dati-rigas-satiksme-sabiedriskajos-transportlidzeklos>

## How it works

1. Data ingestion - monthly .zip files are downloaded from data.gov.lv and extracted
2. Database - extracted .csv (or .txt) data is uploaded and stored in MotherDuck (DuckDB hosted on cloud)
3. Queries - streamlit app connects to MotherDuck, SQL queries are executed and returned as Polars DataFrames
4. Visualization - DataFrames are used to display metrics and charts with Streamlit
5. Deployment - Hosted on Streamlit Community Cloud
