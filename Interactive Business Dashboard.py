import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data
def generate_mock_business_data():
    np.random.seed(42)
    record_count = 1000

    dates = pd.date_range(start="2026-01-01", periods=90, freq="D")
    random_dates = np.random.choice(dates, size=record_count)

    categories = ["Electronics", "Apparel", "Home & Kitchen", "Office Supplies"]
    channels = ["Online Store", "Retail Store", "Mobile App"]

    data = {
        "Transaction_Date": random_dates,
        "Category": np.random.choice(categories, size=record_count),
        "Sales_Channel": np.random.choice(channels, size=record_count, p=[0.5, 0.3, 0.2]),
        "Revenue": np.round(np.random.exponential(scale=150, size=record_count) + 10, 2),
        "Units_Sold": np.random.randint(1, 6, size=record_count),
    }

    df = pd.DataFrame(data)
    df["Cost_of_Goods"] = np.round(df["Revenue"] * np.random.uniform(0.4, 0.6, size=record_count), 2)
    df["Profit"] = df["Revenue"] - df["Cost_of_Goods"]
    return df.sort_values("Transaction_Date").reset_index(drop=True)


st.set_page_config(page_title="Executive Performance Dashboard", layout="wide")

st.title("📊 Enterprise Sales & Profitability Dashboard")
st.markdown("---")

df_raw = generate_mock_business_data()

st.sidebar.header("🎯 Dashboard Filter Pane")

selected_categories = st.sidebar.multiselect(
    "Filter by Product Category",
    options=list(df_raw["Category"].unique()),
    default=list(df_raw["Category"].unique()),
)

selected_channels = st.sidebar.multiselect(
    "Filter by Sales Channel",
    options=list(df_raw["Sales_Channel"].unique()),
    default=list(df_raw["Sales_Channel"].unique()),
)

df_filtered = df_raw[
    (df_raw["Category"].isin(selected_categories)) & (df_raw["Sales_Channel"].isin(selected_channels))
]

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    total_revenue = df_filtered["Revenue"].sum()
    st.metric(label="Gross Revenue", value=f"${total_revenue:,.2f}")

with kpi_col2:
    total_profit = df_filtered["Profit"].sum()
    st.metric(label="Net Profit", value=f"${total_profit:,.2f}")

with kpi_col3:
    margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    st.metric(label="Profit Margin %", value=f"{margin:.1f}%")

with kpi_col4:
    total_items = df_filtered["Units_Sold"].sum()
    st.metric(label="Total Volume (Units)", value=f"{total_items:,}")

st.markdown("---")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📈 Revenue Performance Trajectory")
    timeline_df = df_filtered.groupby("Transaction_Date")["Revenue"].sum().reset_index()
    st.line_chart(data=timeline_df, x="Transaction_Date", y="Revenue", use_container_width=True)

with chart_col2:
    st.subheader("🛍️ Market Share Breakdown by Category")
    category_df = df_filtered.groupby("Category")["Revenue"].sum().reset_index()
    st.bar_chart(data=category_df, x="Category", y="Revenue", use_container_width=True)

st.markdown("---")
st.subheader("🔍 Deep-Dive Operational Ledger View")

show_raw_ledger = st.checkbox("Expand Transaction Audit Log View")

if show_raw_ledger:
    st.dataframe(df_filtered, use_container_width=True)
