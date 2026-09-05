import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Customers", page_icon="👥", layout="wide")

conn = sqlite3.connect("database/manufacturing.db")

customers = pd.read_sql_query(
    "SELECT * FROM customers",
    conn
)

orders = pd.read_sql_query(
    "SELECT * FROM orders",
    conn
)

products = pd.read_sql_query(
    "SELECT * FROM products",
    conn
)

data = orders.merge(
    products[["product_id", "unit_price"]],
    on="product_id",
    how="left"
)

data["revenue"] = (
    data["quantity"] * data["unit_price"]
)

customer_analysis = data.groupby(
    "customer_id"
).agg(
    total_orders=("order_id", "count"),
    units_ordered=("quantity", "sum"),
    revenue=("revenue", "sum")
).reset_index()

customer_analysis = customer_analysis.merge(
    customers,
    on="customer_id",
    how="left"
)

customer_analysis = customer_analysis.sort_values(
    "revenue",
    ascending=False
)

st.title("👥 Customers")

st.subheader("🏆 Top Customers")

st.dataframe(
    customer_analysis,
    use_container_width=True,
    hide_index=True
)

st.subheader("💰 Revenue by Customer")

chart = customer_analysis[
    ["customer_name", "revenue"]
].set_index("customer_name").head(10)

st.bar_chart(chart)

conn.close()