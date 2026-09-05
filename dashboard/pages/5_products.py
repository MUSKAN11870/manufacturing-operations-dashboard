import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Products", page_icon="📊", layout="wide")

conn = sqlite3.connect("database/manufacturing.db")

products = pd.read_sql_query(
    "SELECT * FROM products",
    conn
)

orders = pd.read_sql_query(
    "SELECT * FROM orders",
    conn
)

production = pd.read_sql_query(
    "SELECT * FROM production",
    conn
)

inventory = pd.read_sql_query(
    "SELECT * FROM inventory",
    conn
)

sales = orders.groupby("product_id").agg(
    units_ordered=("quantity", "sum")
).reset_index()

sales = sales.merge(
    products,
    on="product_id",
    how="left"
)

sales["revenue"] = (
    sales["units_ordered"]
    * sales["unit_price"]
)

production_summary = production.merge(
    orders[["order_id", "product_id"]],
    on="order_id",
    how="left"
).groupby("product_id").agg(
    units_produced=("quantity_produced", "sum"),
    defective_units=("defective_quantity", "sum")
).reset_index()

analysis = sales.merge(
    production_summary,
    on="product_id",
    how="left"
)

analysis = analysis.merge(
    inventory[
        ["product_id", "stock_quantity"]
    ],
    on="product_id",
    how="left"
)

analysis["defect_rate"] = (
    analysis["defective_units"]
    / analysis["units_produced"]
    * 100
).fillna(0)

st.title("📊 Products")

st.subheader("Product Performance")

st.dataframe(
    analysis,
    use_container_width=True,
    hide_index=True
)

st.subheader("💰 Revenue by Product")

st.bar_chart(
    analysis[
        ["product_name", "revenue"]
    ].set_index("product_name")
    .sort_values("revenue", ascending=False)
    .head(10)
)

conn.close()