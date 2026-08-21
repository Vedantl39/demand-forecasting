# Demand Forecasting: ARIMA vs. Prophet vs. Holt-Winters

Time-series demand forecasting on real retail sales data — a head-to-head comparison of three classical/modern forecasting methods, plus SQL-based exploratory analysis across 1,115 stores.

## Why this project

Most portfolio projects that touch "time series" pick one method and stop. This one deliberately compares three — Holt-Winters, SARIMA, and Prophet — on the same held-out data with the same evaluation metric, because in practice the choice of method matters less than knowing *when* each is the right tool.

## Executive summary

- **Data:** Rossmann Store Sales (public dataset) — daily sales for 1,115 German drug stores, 2013-01-01 to 2015-07-31.
- **SQL layer:** 7 analysis queries covering day-of-week seasonality, promotion effects, store-type performance, and competition proximity.
- **Forecasting comparison:** trained Holt-Winters, SARIMA, and Prophet on one store's full history (all data except the final 42 days), then evaluated against those actual held-out days.
- **Result:** all three methods land within about half a percentage point of each other (SARIMA: 14.85% MAPE, Holt-Winters: 15.10%, Prophet: 15.32%). The interesting finding isn't "which model wins" — it's that the store's near-deterministic weekly closure pattern (closed every Sunday) is trivially easy for any of the three to learn, while the real differentiator between methods is how tightly each tracks demand *magnitude* on open days.

## Data quality note

The raw `StateHoliday` field had a CSV-quoting artifact that caused the same value (not-a-holiday) to appear as two different categories when read naively — caught and normalized during cleaning (see `src/data_prep.py`).

## Repository structure

```
demand-forecasting/
├── data/
│   ├── raw/                          # Rossmann train.csv, store.csv
│   └── processed/                    # cleaned data, SQLite db, single-store series
├── sql/
│   └── analysis_queries.sql          # 7 SQL analysis queries
├── notebooks/
│   ├── 01_eda.ipynb                  # seasonality, promo effects, monthly trend
│   └── 02_forecasting_comparison.ipynb  # Holt-Winters vs SARIMA vs Prophet
├── src/
│   └── data_prep.py                  # cleaning + SQLite load
├── dashboard/
│   └── app.py                        # Streamlit dashboard
├── reports/                          # exported chart PNGs
└── requirements.txt
```

## Methods used

| Stage | Technique |
|---|---|
| Data layer | SQLite + SQL (aggregations, CASE-based bucketing) |
| EDA | Day-of-week seasonality, promotion lift analysis, monthly trend decomposition |
| Forecasting | Holt-Winters (statsmodels `ExponentialSmoothing`), SARIMA (statsmodels `SARIMAX`), Prophet |
| Evaluation | MAPE and RMSE on a 42-day holdout, computed on open days only (MAPE is undefined at zero actuals) |
| Presentation | Streamlit + Plotly interactive dashboard |

## Running this project

```bash
pip install -r requirements.txt

# 1. Clean the data and build the SQLite db
python src/data_prep.py

# 2. Explore the SQL layer
sqlite3 data/processed/rossmann.db < sql/analysis_queries.sql

# 3. Run the notebooks in order
jupyter notebook notebooks/

# 4. Launch the dashboard
streamlit run dashboard/app.py
```

## Author

Vedant Limaye
