"""
Cleans the raw Rossmann store sales data and prepares it for time-series
forecasting.

Fixes applied:
  - StateHoliday column had a CSV quoting artifact causing the same value
    ("0" / not-a-holiday) to appear as two different categories when read
    naively — normalized to a consistent string type.
  - Only rows where the store was actually open are kept for demand
    modelling (Sales=0 on closed days is a business rule, not a demand
    signal, and would distort a forecasting model if left in).

Writes:
  - data/processed/sales_clean.csv   (all stores, open days only)
  - data/processed/store_daily_full.csv  (one store's full continuous
    daily series, used for the ARIMA/Prophet/Holt-Winters comparison)
"""
import pandas as pd

RAW_SALES = "data/raw/train.csv"
RAW_STORE = "data/raw/store.csv"
OUT_CLEAN = "data/processed/sales_clean.csv"
OUT_SINGLE_STORE = "data/processed/store_daily_full.csv"

FORECAST_STORE_ID = 1  # store with complete 2013-01-01..2015-07-31 history


def main():
    df = pd.read_csv(RAW_SALES, low_memory=False)
    store = pd.read_csv(RAW_STORE, low_memory=False)

    df["StateHoliday"] = df["StateHoliday"].astype(str).str.strip()
    df["Date"] = pd.to_datetime(df["Date"])

    # Keep only open days for the demand series — a closed store isn't "zero demand"
    df_open = df[df["Open"] == 1].copy()

    df_open = df_open.merge(store, on="Store", how="left")
    df_open.to_csv(OUT_CLEAN, index=False)

    single = (
        df[df["Store"] == FORECAST_STORE_ID]
        .sort_values("Date")
        .set_index("Date")
        .asfreq("D")  # forces a continuous daily index; closed days become NaN Sales, filled below
    )
    # Closed days: true zero demand for modelling purposes (store chose not to sell)
    single["Sales"] = single["Sales"].fillna(0)
    single["Open"] = single["Open"].fillna(0)
    single = single.reset_index()

    single.to_csv(OUT_SINGLE_STORE, index=False)

    print(f"Wrote {OUT_CLEAN}: {len(df_open):,} open-day rows across {df_open['Store'].nunique()} stores")
    print(f"Wrote {OUT_SINGLE_STORE}: {len(single)} continuous daily rows for store {FORECAST_STORE_ID}")


if __name__ == "__main__":
    main()
