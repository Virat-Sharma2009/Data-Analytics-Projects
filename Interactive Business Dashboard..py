import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data
def generate_mock_business_data():
    rng = np.random.default_rng(seed=42)
    record_count = 1000
    dates = pd.date_range(start="2026-01-01", periods=90, freq="D")

    categories = ["Electronics", "Apparel", "Home & Kitchen", "Office Supplies"]
    channels = ["Online Store", "Retail Store", "Mobile App"]

    data = {
        "Transaction_Date": rng.choice(dates, size=record_count),
        "Category": rng.choice(categories, size=record_count),
        "Sales_Channel": rng.choice(channels, size=record_count, p=[0.5, 0.3, 0.2]),
        "Revenue": np.round(rng.exponential(scale=150, size=record_count) + 10, 2),
        "Units_Sold": rng.integers(1, 6, size=record_count),
    }

    df = pd.DataFrame(data)
    cost_rate = rng.uniform(0.4, 0.6, size=record_count)
    df["Cost_of_Goods"] = np.round(df["Revenue"] * cost_rate, 2)
    df["Profit"] = df["Revenue"] - df["Cost_of_Goods"]

    return df.sort_values("Transaction_Date").reset_index(drop=True)


st.set_page_config(page_title="Executive Performance Dashboard", layout="wide")
st.title("📊 Enterprise Sales & Profitability Dashboard")
df_raw = generate_mock_business_data()

st.sidebar.header("🎯 Dashboard Filters")

minimum_date = df_raw["Transaction_Date"].min().date()
maximum_date = df_raw["Transaction_Date"].max().date()
selected_date_range = st.sidebar.slider(
    "Transaction date range",
    min_value=minimum_date,
    max_value=maximum_date,
    value=(minimum_date, maximum_date),
    format="YYYY-MM-DD",
)

selected_categories = st.sidebar.multiselect(
    "Product categories",
    options=sorted(df_raw["Category"].unique()),
    default=sorted(df_raw["Category"].unique()),
)

selected_channels = st.sidebar.multiselect(
    "Sales channels",
    options=sorted(df_raw["Sales_Channel"].unique()),
    default=sorted(df_raw["Sales_Channel"].unique()),
)

start_date, end_date = selected_date_range
date_filter = df_raw["Transaction_Date"].dt.date.between(start_date, end_date)
category_filter = df_raw["Category"].isin(selected_categories)
channel_filter = df_raw["Sales_Channel"].isin(selected_channels)
df_filtered = df_raw[date_filter & category_filter & channel_filter]

st.subheader("Executive Summary")
st.caption(
    f"Showing {len(df_filtered):,} of {len(df_raw):,} transactions "
    f"from {start_date:%b %d, %Y} to {end_date:%b %d, %Y}."
)

if df_filtered.empty:
    st.info("No transactions match these filters. Adjust the date range, category, or channel.")
else:
    total_revenue = df_filtered["Revenue"].sum()
    total_profit = df_filtered["Profit"].sum()
    total_units = df_filtered["Units_Sold"].sum()
    profit_margin = total_profit / total_revenue * 100 if total_revenue else 0

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Gross Revenue", f"${total_revenue:,.2f}")
    kpi_col2.metric("Gross Profit", f"${total_profit:,.2f}")
    kpi_col3.metric("Profit Margin", f"{profit_margin:.1f}%")
    kpi_col4.metric("Units Sold", f"{total_units:,}")

    st.markdown("---")

    trend_col, category_col = st.columns(2)

    with trend_col:
        st.subheader("📈 Revenue Over Time")
        daily_revenue = (
            df_filtered.groupby("Transaction_Date", as_index=False)["Revenue"]
            .sum()
            .sort_values("Transaction_Date")
        )
        st.line_chart(
            data=daily_revenue,
            x="Transaction_Date",
            y="Revenue",
            use_container_width=True,
        )

    with category_col:
        st.subheader("🛍️ Revenue by Product Category")
        category_revenue = (
            df_filtered.groupby("Category", as_index=False)["Revenue"]
            .sum()
            .sort_values("Revenue", ascending=False)
        )
        st.bar_chart(
            data=category_revenue,
            x="Category",
            y="Revenue",
            use_container_width=True,
        )

    st.subheader("🏬 Revenue by Sales Channel")
    channel_revenue = (
        df_filtered.groupby("Sales_Channel", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    st.bar_chart(
        data=channel_revenue,
        x="Sales_Channel",
        y="Revenue",
        use_container_width=True,
    )

    with st.expander("🔍 View and download filtered transactions"):
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download filtered transactions as CSV",
            data=csv_data,
            file_name="filtered_business_transactions.csv",
            mime="text/csv",
        )
