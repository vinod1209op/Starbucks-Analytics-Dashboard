#Starbucks Ecommerce Analytics Dashboard using Streamlit, Faker, Pandas, and Plotly
import streamlit as st
import pandas as pd
import plotly.express as px
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np
st.set_page_config(
    page_title="Starbucks Ecommerce Analytics Dashboard",
    page_icon=":coffee:",
    layout="wide"
)
st.title("Starbucks Ecommerce Analytics Dashboard")
st.markdown("This dashboard presents synthetic ecommerce data for Starbucks.")
@st.cache_data
def generate_synthetic_data(num_records: int) -> pd.DataFrame:
    fake = Faker()
    data = []
    start_date = datetime(2023, 1, 1)
    for _ in range(num_records):
        order_date = start_date + timedelta(days=random.randint(0, 364))
        data.append({
            "Order ID": fake.uuid4(),
            "Customer ID": fake.uuid4(),
            "Product": random.choice(["Coffee", "Tea", "Pastry", "Merchandise"]),
            "Category": random.choice(["Beverages", "Food", "Accessories"]),
            "Quantity": random.randint(1, 5),
            "Price": round(random.uniform(2.5, 15.0), 2),
            "Order Date": order_date,
            "Region": random.choice(["North America", "Europe", "Asia", "South America"]),
        })
    df = pd.DataFrame(data)
    df["Total Sales"] = df["Quantity"] * df["Price"]
    return df
df = generate_synthetic_data(1000)
with st.expander("View Sample DataFrame"):
    st.dataframe(df.head(10))
# Sales Over Time Line Chart
sales_over_time = df.groupby(df["Order Date"].dt.to_period("M")).agg({"Total Sales": "sum"}).reset_index()
sales_over_time["Order Date"] = sales_over_time["Order Date"].dt.to_timestamp()
fig_sales_time = px.line(
    sales_over_time,
    x="Order Date",
    y="Total Sales",
    title="Total Sales Over Time",
    labels={"Order Date": "Order Date", "Total Sales": "Total Sales ($)"},
    markers=True
)
st.plotly_chart(fig_sales_time, use_container_width=True)
# Sales by Product Category Bar Chart
sales_by_category = df.groupby("Category").agg({"Total Sales": "sum"}).reset_index()
fig_sales_category = px.bar(
    sales_by_category,
    x="Category",
    y="Total Sales",
    title="Total Sales by Product Category",
    labels={"Category": "Product Category", "Total Sales": "Total Sales ($)"},
    color="Category"
)
st.plotly_chart(fig_sales_category, use_container_width=True)
# Sales by Region Pie Chart
sales_by_region = df.groupby("Region").agg({"Total Sales": "sum"}).reset_index()
fig_sales_region = px.pie(
    sales_by_region,
    names="Region",
    values="Total Sales",
    title="Sales Distribution by Region"
)
st.plotly_chart(fig_sales_region, use_container_width=True)
# Average Order Value KPI
average_order_value = df["Total Sales"].mean()
st.metric(label="Average Order Value", value=f"${average_order_value:.2f}")
# Total Sales KPI
total_sales = df["Total Sales"].sum()
st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
# Total Orders KPI
total_orders = df["Order ID"].nunique()
st.metric(label="Total Orders", value=f"{total_orders}")
# Monthly Sales Growth KPI
monthly_sales = df.groupby(df["Order Date"].dt.to_period("M")).agg({"Total Sales": "sum"}).reset_index()
monthly_sales["Order Date"] = monthly_sales["Order Date"].dt.to_timestamp()
monthly_sales["Sales Growth"] = monthly_sales["Total Sales"].pct_change().fillna(0)
latest_growth = monthly_sales.iloc[-1]["Sales Growth"] * 100
st.metric(label="Monthly Sales Growth", value=f"{latest_growth:.2f}%")
# Customer Acquisition Over Time Line Chart
customer_acquisition = df.groupby(df["Order Date"].dt.to_period("M")).agg({"Customer ID": pd.Series.nunique}).reset_index()
customer_acquisition["Order Date"] = customer_acquisition["Order Date"].dt.to_timestamp()
fig_customer_acquisition = px.line(
    customer_acquisition,
    x="Order Date",
    y="Customer ID",
    title="Customer Acquisition Over Time",
    labels={"Order Date": "Order Date", "Customer ID": "Number of New Customers"},
    markers=True
)
st.plotly_chart(fig_customer_acquisition, use_container_width=True)


