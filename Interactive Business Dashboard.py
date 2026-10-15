import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data
def generate_mock_business_data():
    # WHAT: Generates an artificial, clean dataset of 1,000 retail sales transactions.
    # HOW: Creates a repeatable pseudo-random date sequence, categories, revenue totals, and channels.
    # WHY: Gives us immediate data to build an enterprise-level portfolio project without requiring external database keys.
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


# ------------------------------------------------------------------------------
# APPLICATION LAYOUT & INITIALIZATION
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Executive Performance Dashboard", layout="wide")
# WHAT: Configures the browser window title and stretches the container across the entire viewport.
# HOW: Calls Streamlit's structural configuration utility right at initialization.
# WHY: Dashboards require a 'wide' landscape aspect ratio to show multiple charts side-by-side cleanly.

st.title("📊 Enterprise Sales & Profitability Dashboard")
st.markdown("---")

df_raw = generate_mock_business_data()

# ------------------------------------------------------------------------------
# SIDEBAR FILTERS (USER INTERACTIVITY)
# ------------------------------------------------------------------------------

st.sidebar.header("🎯 Dashboard Filter Pane")
# WHAT: Creates a persistent, slide-out configuration sidebar on the left side of the screen.
# HOW: Uses the 'st.sidebar' workspace layout namespace.
# WHY: Isolates configuration controls from core analytical charts, matching standard BI layouts.

selected_categories = st.sidebar.multiselect(
    "Filter by Product Category",
    options=list(df_raw["Category"].unique()),
    default=list(df_raw["Category"].unique()),
)
# WHAT: Creates an interactive multi-choice dropdown listing all product lines.
# HOW: Uses 'st.sidebar.multiselect' to capture user choices as a Python list.
# WHY: Allows executives to drill down into specific segments (e.g., assessing Electronics vs. Apparel).

selected_channels = st.sidebar.multiselect(
    "Filter by Sales Channel",
    options=list(df_raw["Sales_Channel"].unique()),
    default=list(df_raw["Sales_Channel"].unique()),
)

# ------------------------------------------------------------------------------
# DATA INTERSECTION & SLICING
# ------------------------------------------------------------------------------

df_filtered = df_raw[
    (df_raw["Category"].isin(selected_categories)) & (df_raw["Sales_Channel"].isin(selected_channels))
]
# WHAT: Dynamically slices the master DataFrame based on current sidebar variables.
# HOW: Uses pandas vector boolean masking evaluation filters.
# WHY: Ensures that every single card, metric, and graph re-renders instantly to match user choices.

# ------------------------------------------------------------------------------
# EXECUTIVE KPI SUMMARY CARDS
# ------------------------------------------------------------------------------

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
# WHAT: Divides the horizontal layout space into 4 evenly spaced columns.
# HOW: Uses the structural grid layout utility function 'st.columns(4)'.
# WHY: Matches classic executive operational dashboard layouts by highlighting fundamental health metrics on top.

with kpi_col1:
    total_revenue = df_filtered["Revenue"].sum()
    st.metric(label="Gross Revenue", value=f"${total_revenue:,.2f}")
    # WHAT: Renders a large-format business metric snapshot container.
    # HOW: Aggregates the column values and formats them with string currency commas.
    # WHY: Instantly conveys top-line financial performance to the user.

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

# ------------------------------------------------------------------------------
# SYSTEM METRIC CHARTS & REVENUE TIMELINES
# ------------------------------------------------------------------------------

chart_col1, chart_col2 = st.columns(2)
# WHAT: Splitting the lower layout canvas into two matching grid structures.
# HOW: Instantiates a two-column context array layout.
# WHY: Allows us to show a timeline and a categorical share breakdown on the same row.

with chart_col1:
    st.subheader("📈 Revenue Performance Trajectory")
    timeline_df = df_filtered.groupby("Transaction_Date")["Revenue"].sum().reset_index()
    st.line_chart(data=timeline_df, x="Transaction_Date", y="Revenue", use_container_width=True)
    # WHAT: Draws an interactive time-series line chart of revenue trends.
    # HOW: Groups the sliced data structure by date and invokes the native vector 'st.line_chart' utility.
    # WHY: Proves to a recruiter you can track seasonal trends, momentum shift points, and revenue volatility.

with chart_col2:
    st.subheader("🛍️ Market Share Breakdown by Category")
    category_df = df_filtered.groupby("Category")["Revenue"].sum().reset_index()
    st.bar_chart(data=category_df, x="Category", y="Revenue", use_container_width=True)
    # WHAT: Draws a distinct structural comparison bar chart of total performance across category clusters.
    # HOW: Aggregates revenue allocations and streams them directly into 'st.bar_chart'.
    # WHY: Instantly shows which business sectors are driving the vast majority of consumer purchases.

# ------------------------------------------------------------------------------
# AUDIT LOG DATA EXPLORATION LAYER
# ------------------------------------------------------------------------------

st.markdown("---")
st.subheader("🔍 Deep-Dive Operational Ledger View")

show_raw_ledger = st.checkbox("Expand Transaction Audit Log View")
# WHAT: Creates an on-demand interactive checkbox toggle layout block.
# HOW: Wraps a conditional Python block around an 'st.checkbox' boolean engine evaluation.
# WHY: Prevents the screen from feeling cluttered, but gives engineers or financial controllers immediate raw-data validation visibility.

if show_raw_ledger:
    st.dataframe(df_filtered, use_container_width=True)
    # WHAT: Renders a scalable, interactive, sortable data grid display pane.
    # HOW: Hands our processed DataFrame straight into 'st.dataframe'.
    # WHY: Empowers operators to run on-screen column sorting, individual rows evaluation, and precise numerical validation.
