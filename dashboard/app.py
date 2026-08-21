"""
Demand Forecasting Dashboard — Rossmann Store Sales

Run with:
    streamlit run dashboard/app.py
"""
import sqlite3
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

st.set_page_config(page_title="Demand Forecasting", page_icon="chart", layout="wide")


@st.cache_data
def load_data():
    conn = sqlite3.connect(DATA_DIR / "rossmann.db")
    sales = pd.read_sql_query("SELECT * FROM sales", conn, parse_dates=["Date"])
    conn.close()
    store1 = pd.read_csv(DATA_DIR / "store_daily_full.csv", parse_dates=["Date"])
    return sales, store1


sales, store1 = load_data()

st.title("Demand Forecasting Analytics")
st.caption(
    "Rossmann Store Sales — daily sales for 1,115 stores, 2013\u20132015 (public dataset). "
    "SQL + Python analysis, with a head-to-head ARIMA / Prophet / Holt-Winters "
    "forecast comparison for a single store."
)

tab1, tab2, tab3 = st.tabs(["Sales overview", "Store comparison", "Forecast comparison"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total stores", f"{sales['Store'].nunique():,}")
    c2.metric("Date range", "2013-01 to 2015-07")
    c3.metric("Avg daily sales/store", f"{sales['Sales'].mean():,.0f}")
    c4.metric("Avg daily customers/store", f"{sales['Customers'].mean():,.0f}")

    left, right = st.columns(2)
    with left:
        dow_names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
        dow = sales.groupby("DayOfWeek")["Sales"].mean().rename(index=dow_names).reset_index()
        fig1 = px.bar(dow, x="DayOfWeek", y="Sales", title="Average sales by day of week")
        st.plotly_chart(fig1, use_container_width=True)

    with right:
        promo = sales.groupby(["StoreType", "Promo"])["Sales"].mean().reset_index()
        promo["Promo"] = promo["Promo"].map({0: "No promo", 1: "Promo"})
        fig2 = px.bar(
            promo, x="StoreType", y="Sales", color="Promo", barmode="group",
            title="Promotion effect on sales, by store type",
        )
        st.plotly_chart(fig2, use_container_width=True)

    monthly = sales.set_index("Date").resample("MS")["Sales"].sum().reset_index()
    fig3 = px.line(monthly, x="Date", y="Sales", title="Aggregate monthly sales, all stores", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    store_type_summary = (
        sales.groupby(["StoreType", "Assortment"])
        .agg(num_stores=("Store", "nunique"), avg_daily_sales=("Sales", "mean"))
        .reset_index()
    )
    fig4 = px.bar(
        store_type_summary, x="StoreType", y="avg_daily_sales", color="Assortment",
        barmode="group", title="Average daily sales by store type and assortment level",
    )
    st.plotly_chart(fig4, use_container_width=True)

    top_stores = (
        sales.groupby("Store").agg(days_open=("Sales", "count"), avg_daily_sales=("Sales", "mean"))
        .query("days_open >= 900")
        .sort_values("avg_daily_sales", ascending=False)
        .head(15)
        .reset_index()
    )
    fig5 = px.bar(top_stores, x="Store", y="avg_daily_sales", title="Top 15 highest-volume stores")
    fig5.update_xaxes(type="category")
    st.plotly_chart(fig5, use_container_width=True)

with tab3:
    st.markdown(
        "Forecast comparison for **Store 1** (chosen for having complete, continuous "
        "daily history over the full period). Models were trained on all data except "
        "the final 42 days, then evaluated against those actual held-out values. "
        "Full methodology in `notebooks/02_forecasting_comparison.ipynb`."
    )

    results = pd.DataFrame({
        "model": ["Holt-Winters", "SARIMA", "Prophet"],
        "MAPE_%": [15.10, 14.85, 15.32],
        "RMSE": [769.0, 773.4, 773.4],
    }).set_index("model")

    c1, c2, c3 = st.columns(3)
    c1.metric("Holt-Winters MAPE", f"{results.loc['Holt-Winters','MAPE_%']}%")
    c2.metric("SARIMA MAPE", f"{results.loc['SARIMA','MAPE_%']}%", delta="best", delta_color="off")
    c3.metric("Prophet MAPE", f"{results.loc['Prophet','MAPE_%']}%")

    st.dataframe(results)

    st.info(
        "All three methods land within about half a percentage point of each other on "
        "this store's data — the interesting result here is less 'which model wins' and "
        "more that the weekly closure pattern (Sundays) is easy for any of them to learn, "
        "while the real differentiator is how tightly each tracks demand magnitude on open days."
    )

    fig6 = go.Figure()
    recent = store1.tail(120)
    fig6.add_trace(go.Scatter(x=recent["Date"], y=recent["Sales"], mode="lines", name="Actual sales"))
    fig6.update_layout(title="Store 1 — last 120 days of actual daily sales", xaxis_title="Date", yaxis_title="Sales")
    st.plotly_chart(fig6, use_container_width=True)
