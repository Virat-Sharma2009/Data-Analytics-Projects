import numpy as np
import pandas as pd
import streamlit as st


# INTERVIEW TALK TRACK:
# "I started by importing NumPy for reproducible sample data, pandas for tabular
# analysis, and Streamlit for the interactive web application."

# WHAT: Builds realistic-looking retail transactions for the dashboard to analyze.
# HOW: Uses a local random-number generator with a fixed seed, so every rerun creates
#      the same sample data without changing NumPy's random state elsewhere.
# WHY: A consistent sample dataset makes the dashboard immediately usable and makes
#      its numbers easy to compare while learning. Replace this function with a real
#      database or file import when you have business data to connect.
# INTERVIEW TALK TRACK:
# "Because I didn't connect real company data, I generated sample transactions.
# I used a fixed seed so the sample results are repeatable when I demonstrate it."
@st.cache_data
def generate_mock_business_data():
    # WHAT: Sets the sample size and the dates used by the generated transactions.
    # HOW: Creates 90 calendar dates and asks the random generator for 1,000 records.
    # WHY: This gives the dashboard enough data to show trends and segments.
    rng = np.random.default_rng(seed=42)
    record_count = 1000
    dates = pd.date_range(start="2026-01-01", periods=90, freq="D")

    # WHAT: Defines the business segments available in the generated dataset.
    # HOW: Stores category and channel labels in lists for random selection.
    # WHY: These segment values are also the options used by the interactive filters.
    categories = ["Electronics", "Apparel", "Home & Kitchen", "Office Supplies"]
    channels = ["Online Store", "Retail Store", "Mobile App"]

    # WHAT: Stores one row per sale, with the fields used by the dashboard.
    # HOW: Selects a date, product category, sales channel, revenue, and unit count
    #      for each transaction; then derives cost and profit from revenue.
    # WHY: Keeping the data in a DataFrame lets pandas filter and summarize all
    #      transactions consistently for both the KPI cards and charts.
    data = {
        "Transaction_Date": rng.choice(dates, size=record_count),
        "Category": rng.choice(categories, size=record_count),
        "Sales_Channel": rng.choice(channels, size=record_count, p=[0.5, 0.3, 0.2]),
        "Revenue": np.round(rng.exponential(scale=150, size=record_count) + 10, 2),
        "Units_Sold": rng.integers(1, 6, size=record_count),
    }

    # WHAT: Converts generated values into a transaction table and derives cost/profit.
    # HOW: Creates a pandas DataFrame, assigns a cost rate between 40% and 60%,
    #      then subtracts cost of goods from revenue.
    # WHY: A consistent table structure makes filtering and aggregation straightforward.
    df = pd.DataFrame(data)
    cost_rate = rng.uniform(0.4, 0.6, size=record_count)
    df["Cost_of_Goods"] = np.round(df["Revenue"] * cost_rate, 2)
    df["Profit"] = df["Revenue"] - df["Cost_of_Goods"]

    # WHAT: Returns transactions in date order with a clean sequential row index.
    # HOW: Sorts by transaction date and resets the index after sorting.
    # WHY: Chronological data is easier to inspect and use for the revenue trend.
    return df.sort_values("Transaction_Date").reset_index(drop=True)


# WHAT: Sets up the browser tab and the wide page layout before any dashboard content.
# HOW: Streamlit applies page configuration at the start of the script, then renders
#      the title and a short explanation for the user.
# WHY: A wide layout leaves enough room for business metrics and charts side by side.
# INTERVIEW TALK TRACK:
# "I set the page to a wide layout because this dashboard compares several metrics
# and charts. I also tell the user up front that the data is simulated."
st.set_page_config(page_title="Executive Performance Dashboard", layout="wide")
st.title("📊 Enterprise Sales & Profitability Dashboard")
st.caption(
    "Explore sample retail performance by date, product category, and sales channel. "
    "The included transactions are simulated, not real business results."
)

# WHAT: Provides a concise explanation of the portfolio project for an interviewer.
# HOW: Uses an expandable Streamlit section to present the goal, tools, workflow,
#      and limitations without taking up space in the main dashboard.
# WHY: Helps a reviewer understand the decisions behind the project while accurately
#      distinguishing a portfolio demo from production reporting.
# INTERVIEW TALK TRACK:
# "I included a project walkthrough in the app so a reviewer can understand the
# business question, technical approach, and what I would improve for production."
with st.expander("💼 Project walkthrough (portfolio explanation)"):
    st.markdown(
        """
        **How I describe this project**

        > I built this interactive business dashboard as a portfolio project to
        > explore how retail sales and profitability can be summarized for
        > decision-makers. I used Python, pandas, NumPy, and Streamlit to create
        > sample transaction data, let users filter it, and update the metrics
        > and charts based on their selections.

        **The business question**

        A manager needs a quick way to see how revenue, profit, and sales volume
        change over time and across product categories and sales channels. This
        dashboard brings those views together and lets the user narrow the
        analysis with date and category filters.

        **How it works**

        - NumPy generates reproducible example transactions; pandas stores and
          summarizes them in a DataFrame.
        - Streamlit provides the interactive date, category, and channel filters.
        - The selected rows drive the KPI cards, revenue charts, transaction
          table, and CSV download.
        - The app handles an empty filter result with a message instead of
          attempting to draw empty summaries.

        **What I would improve next**

        The data is simulated, so the dashboard is a demonstration and not a
        source of real business reporting. For a production version, I would
        connect a validated data source, confirm metric definitions with
        stakeholders, and include other operating expenses before reporting
        net profit. The current profit calculation subtracts cost of goods sold
        from revenue, so it represents gross profit.
        """
    )

st.markdown("---")

df_raw = generate_mock_business_data()


# WHAT: Creates controls for narrowing the transactions included in the analysis.
# HOW: Streamlit returns each selection as the user changes a control; the script
#      reruns automatically and uses the latest values below.
# WHY: Interactive filters let a user answer focused questions without editing code.
# INTERVIEW TALK TRACK:
# "Next, I build the sidebar controls. Streamlit reruns the script when selections
# change, so the dashboard updates from the same source data."
st.sidebar.header("🎯 Dashboard Filters")

# WHAT: Finds the earliest and latest dates available in the sample.
# HOW: Gets the minimum and maximum transaction dates, then converts them to dates.
# WHY: These values set safe boundaries for the date-range slider.
minimum_date = df_raw["Transaction_Date"].min().date()
maximum_date = df_raw["Transaction_Date"].max().date()

# WHAT: Lets the user choose the time period to analyze.
# HOW: Sets the slider bounds to the available dates and defaults to the full period.
# WHY: A date range makes it possible to compare performance over selected periods.
selected_date_range = st.sidebar.slider(
    "Transaction date range",
    min_value=minimum_date,
    max_value=maximum_date,
    value=(minimum_date, maximum_date),
    format="YYYY-MM-DD",
)

# WHAT: Lets the user include one or more product categories.
# HOW: Uses distinct sorted category names as options and selects all initially.
# WHY: Sorting improves usability; selecting all gives a complete default view.
selected_categories = st.sidebar.multiselect(
    "Product categories",
    options=sorted(df_raw["Category"].unique()),
    default=sorted(df_raw["Category"].unique()),
)

# WHAT: Lets the user include one or more sales channels.
# HOW: Uses distinct sorted channel names as options and selects all initially.
# WHY: Users can compare online, retail, and mobile activity without changing code.
selected_channels = st.sidebar.multiselect(
    "Sales channels",
    options=sorted(df_raw["Sales_Channel"].unique()),
    default=sorted(df_raw["Sales_Channel"].unique()),
)


# WHAT: Applies every selected filter to produce the transactions being analyzed.
# HOW: Combines pandas boolean conditions for the inclusive date range, category
#      selection, and sales-channel selection.
# WHY: Using one filtered DataFrame keeps every KPI, chart, and data-table result
#      aligned with the same choices in the sidebar.
# INTERVIEW TALK TRACK:
# "I create a separate true-or-false filter for each selection, then combine them.
# That gives all dashboard sections one consistent set of matching transactions."
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

# WHAT: Handles the case where the user's filters exclude every transaction.
# HOW: Tests whether the filtered DataFrame has any rows and shows an explanatory
#      message instead of attempting to calculate or chart empty data.
# WHY: This makes the app clearer and avoids misleading or confusing blank results.
if df_filtered.empty:
    # WHAT: Explains why the summary and charts have no results.
    # HOW: Checks the filtered DataFrame before calculating metrics or drawing charts.
    # WHY: Clear feedback helps users recover by changing one or more sidebar filters.
    st.info("No transactions match these filters. Adjust the date range, category, or channel.")
else:
    # WHAT: Calculates the headline performance indicators for the selected sales.
    # HOW: Sums revenue, profit, and units, then calculates margin as profit divided
    #      by revenue; the guard avoids division by zero for any future data source.
    # WHY: These KPIs summarize sales scale, profitability, and volume at a glance.
    total_revenue = df_filtered["Revenue"].sum()
    total_profit = df_filtered["Profit"].sum()
    total_units = df_filtered["Units_Sold"].sum()
    profit_margin = total_profit / total_revenue * 100 if total_revenue else 0

    # WHAT: Places four key performance indicators in a single dashboard row.
    # HOW: Creates four Streamlit columns and formats each calculated value for display.
    # WHY: Decision-makers can scan revenue, gross profit, margin, and volume quickly.
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Gross Revenue", f"${total_revenue:,.2f}")
    kpi_col2.metric("Gross Profit", f"${total_profit:,.2f}")
    kpi_col3.metric("Profit Margin", f"{profit_margin:.1f}%")
    kpi_col4.metric("Units Sold", f"{total_units:,}")

    st.markdown("---")

    # WHAT: Shows how revenue changes over time and how it is distributed by segment.
    # HOW: Groups the filtered transactions by date, category, and channel, summing
    #      revenue within each group before passing the summaries to Streamlit charts.
    # WHY: The trend makes timing patterns visible, while segment charts help compare
    #      the product lines and routes to market contributing to revenue.
    # INTERVIEW TALK TRACK:
    # "I aggregate only the filtered transactions. The line chart shows daily revenue,
    # and the bar charts compare revenue by category and channel."
    trend_col, category_col = st.columns(2)

    with trend_col:
        # WHAT: Summarizes revenue at daily level for the trend chart.
        # HOW: Groups rows by transaction date, sums revenue, and sorts dates ascending.
        # WHY: One total per date makes changes in revenue easier to see over time.
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
        # WHAT: Summarizes revenue for each product category.
        # HOW: Groups by category, totals revenue, and orders categories highest first.
        # WHY: This makes category performance easy to compare.
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

    # WHAT: Summarizes revenue for each sales channel.
    # HOW: Groups by channel, totals revenue, and sorts channels by revenue.
    # WHY: This helps identify which route to market contributes most in the selection.
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

    # WHAT: Provides access to the transactions behind the summary and a CSV export.
    # HOW: Shows a sortable Streamlit data grid in an expandable section and converts
    #      the currently filtered rows to CSV for the download button.
    # WHY: Users can validate the summaries, inspect individual records, or continue
    #      their analysis in a spreadsheet without exporting unrelated transactions.
    # INTERVIEW TALK TRACK:
    # "I finish with transaction-level detail and a CSV export, so users can inspect
    # the records behind the summaries and reuse just the data they selected."
    with st.expander("🔍 View and download filtered transactions"):
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        # WHAT: Converts the visible filtered transactions into downloadable CSV data.
        # HOW: Serializes the DataFrame without its row index and encodes it as UTF-8.
        # WHY: CSV is a common format for sharing and continuing analysis in a spreadsheet.
        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download filtered transactions as CSV",
            data=csv_data,
            file_name="filtered_business_transactions.csv",
            mime="text/csv",
        )
