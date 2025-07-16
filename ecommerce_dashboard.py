# ecommerce_dashboard.py
# Author: Amin Keyvanloo
# Date: [2025-07-15]
# Description: Interactive E-commerce Sales Dashboard using Streamlit
# Features: Filters, KPIs, Trend Charts, Category Insights, Data Download, Feedback Form

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from datetime import datetime
import os

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# ---------------------- TITLE & INTRO ----------------------
st.title("📊 E-commerce Sales Analytics Dashboard")
st.write("""
Welcome to the E-commerce Sales Dashboard – an interactive platform designed to help you explore, analyze, 
and gain insights from sales performance data. Filter by region, segment, and date to reveal key patterns, 
compare product profitability, and track customer behavior.
""")

# ---------------------- SIDEBAR: LOGO ----------------------
logo = Image.open("assets/logo.png")
st.sidebar.image(logo, use_container_width=True)

# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data():
    """Load and prepare the dataset."""
    df = pd.read_csv("ecommerce_data.csv", parse_dates=["Order Date", "Ship Date"])
    df["Delivery Time"] = (df["Ship Date"] - df["Order Date"]).dt.days
    return df

df = load_data()

# ---------------------- SIDEBAR: FILTERS ----------------------
st.sidebar.header("🔎 Filter Data")

# Date range
min_date, max_date = df["Order Date"].min(), df["Order Date"].max()
date_range = st.sidebar.date_input("📅 Order Date Range", [min_date, max_date])

# Segment filter
segments = df["Segment"].unique()
selected_segments = st.sidebar.multiselect("Select Customer Segment", options=segments, default=[])

# Region filter
regions = df["Region"].unique()
selected_regions = st.sidebar.multiselect("Select Region", options=regions, default=[])

# Validation
if not selected_segments or not selected_regions:
    st.warning("⚠️ Please select at least one Segment and one Region to proceed.")
    st.stop()

# Filter data
filtered_df = df[
    (df["Order Date"] >= pd.to_datetime(date_range[0])) &
    (df["Order Date"] <= pd.to_datetime(date_range[1])) &
    (df["Segment"].isin(selected_segments)) &
    (df["Region"].isin(selected_regions))
]

# ---------------------- SIDEBAR: TOGGLES ----------------------
st.sidebar.header("📊 Show/Hide Charts")
show_region_chart = st.sidebar.checkbox("Sales by Region")
show_category_chart = st.sidebar.checkbox("Sales by Category")
show_top_products_chart = st.sidebar.checkbox("Top Products by Profit")
show_segment_chart = st.sidebar.checkbox("Customer Segment Breakdown")

# ---------------------- RAW DATA ----------------------
with st.expander("📂 Show Raw Data"):
    st.dataframe(filtered_df)

# ---------------------- KPIs ----------------------
st.markdown("### 🔑 Key Metrics (Filtered vs Overall)")

# Metrics
overall_sales = df["Sales"].sum()
overall_profit = df["Profit"].sum()
overall_orders = df["Order ID"].nunique()
overall_delivery = df["Delivery Time"].mean()

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()
avg_delivery = filtered_df["Delivery Time"].mean()

# Deltas
sales_delta = ((total_sales - overall_sales) / overall_sales) * 100
profit_delta = ((total_profit - overall_profit) / overall_profit) * 100
orders_delta = ((total_orders - overall_orders) / overall_orders) * 100
delivery_delta = avg_delivery - overall_delivery

# Display
col1, col2, col3, col4 = st.columns(4)
col1.metric("🛒 Total Sales", f"${total_sales:,.2f}", f"{sales_delta:.2f}%")
col2.metric("💰 Total Profit", f"${total_profit:,.2f}", f"{profit_delta:.2f}%")
col3.metric("📦 Total Orders", total_orders, f"{orders_delta:.2f}%")
col4.metric("⏱️ Avg Delivery Time", f"{avg_delivery:.2f} days", f"{delivery_delta:+.2f} days")

# ---------------------- TREND CHART ----------------------
st.markdown("### 📈 Sales and Profit Trend Over Time")

# Time granularity selection
time_granularity = st.radio(
    "Select Time Granularity", options=["Monthly", "Daily"],
    horizontal=True, key="time_granularity_radio"
)

# Prepare time data
if time_granularity == "Monthly":
    time_data = filtered_df.set_index("Order Date").resample("M")[["Sales", "Profit"]].sum().reset_index()
else:
    time_data = filtered_df.set_index("Order Date").resample("D")[["Sales", "Profit"]].sum().reset_index()

# Plot trend
fig, ax = plt.subplots(figsize=(10, 4))
sns.lineplot(data=time_data, x="Order Date", y="Sales", label="Sales", marker="o", color="dodgerblue")
sns.lineplot(data=time_data, x="Order Date", y="Profit", label="Profit", marker="o", color="salmon")
ax.set_title(f"{time_granularity} Sales & Profit Trend")
ax.set_xlabel("Order Date")
ax.set_ylabel("Amount ($)")
plt.xticks(rotation=45)
st.pyplot(fig)

# ---------------------- OPTIONAL CHARTS ----------------------
if show_region_chart:
    st.subheader("🌍 Sales by Region")
    region_sales = filtered_df.groupby("Region")["Sales"].sum().reset_index().sort_values(by="Sales", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 3))
    sns.barplot(data=region_sales, x="Sales", y="Region", palette="Greens_d", ax=ax)
    ax.set_title("Sales by Region")
    st.pyplot(fig)

if show_category_chart:
    st.subheader("🧱 Sales by Category")
    category_sales = filtered_df.groupby("Category")["Sales"].sum().reset_index().sort_values(by="Sales", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 3))
    sns.barplot(data=category_sales, x="Sales", y="Category", palette="Blues_d", ax=ax)
    ax.set_title("Sales by Category")
    st.pyplot(fig)

if show_top_products_chart:
    st.subheader("💎 Top 10 Products by Profit")
    top_products = (
        filtered_df.groupby("Product Name")["Profit"]
        .sum().sort_values(ascending=False).head(10).reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.barplot(data=top_products, y="Product Name", x="Profit", palette="coolwarm", ax=ax)
    ax.set_title("Top 10 Most Profitable Products")
    st.pyplot(fig)

if show_segment_chart:
    st.subheader("👥 Sales & Profit by Customer Segment")
    segment_summary = (
        filtered_df.groupby("Segment")[["Sales", "Profit"]]
        .sum().sort_values(by="Sales", ascending=False).reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 3))
    segment_summary.plot(kind='barh', x='Segment', stacked=False, ax=ax, color=['skyblue', 'salmon'])
    ax.set_title("Sales and Profit by Customer Segment")
    st.pyplot(fig)

# ---------------------- PREFERRED CATEGORIES BY SEGMENT ----------------------
st.subheader("🎯 Preferred Categories by Customer Segment")
segment_category = (
    filtered_df.groupby(["Segment", "Category"])["Sales"]
    .sum().reset_index()
)
fig = plt.figure(figsize=(10, 3))
sns.barplot(data=segment_category, x="Sales", y="Category", hue="Segment", dodge=True)
plt.title("Top Categories Purchased by Customer Segment")
st.pyplot(fig)

# ---------------------- DOWNLOAD DATA ----------------------
st.markdown("### 📥 Download Filtered Data")

@st.cache_data
def convert_df_to_csv(df):
    """Convert DataFrame to downloadable CSV."""
    return df.to_csv(index=False).encode("utf-8")

csv_data = convert_df_to_csv(filtered_df)
st.download_button(
    label="⬇️ Download CSV",
    data=csv_data,
    file_name="filtered_data.csv",
    mime="text/csv"
)

# ---------------------- FEEDBACK SECTION ----------------------
st.markdown("---")
st.markdown("## 💬 Feedback")

feedback = st.text_area("What do you think about this dashboard?", placeholder="Write your comments here...")

if st.button("Submit Feedback"):
    if feedback.strip():
        file_path = "feedback.csv"
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("Timestamp,Feedback\n")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp},{feedback.replace(',', ';')}\n")

        st.success("✅ Thank you! Your feedback has been received.")
    else:
        st.warning("⚠️ Please enter some feedback before submitting.")

with st.expander("📬 View Submitted Feedback"):
    if os.path.exists("feedback.csv"):
        feedback_df = pd.read_csv("feedback.csv")
        st.dataframe(feedback_df)
    else:
        st.info("No feedback submitted yet.")
