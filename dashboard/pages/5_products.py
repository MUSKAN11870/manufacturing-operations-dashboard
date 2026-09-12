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
import uuid

st.subheader("➕ Add New Product")
with st.form("add_product_form", clear_on_submit=True):
    product_id = st.text_input("Product ID (e.g. ball1, bat2 — use this exact ID in Orders/Production/Stock)")
    product_name = st.text_input("Product Name")
    category = st.text_input("Category")
    unit_price = st.number_input("Unit Price", min_value=0, step=1)
    reorder_level = st.number_input("Reorder Level", min_value=0, step=1)
    submitted = st.form_submit_button("Add Product")

    if submitted:
        conn2 = sqlite3.connect("database/manufacturing.db")
        conn2.execute(
            "INSERT INTO products (product_id, product_name, category, unit_price, reorder_level, source) VALUES (?, ?, ?, ?, ?, 'real')",
            (product_id, product_name, category, unit_price, reorder_level)
        )
        conn2.commit()
        conn2.close()
        st.success(f"Product '{product_name}' added with ID {product_id}!")
        st.rerun()

with st.expander("🧹 Manage example data"):
    if st.button("Delete all example products"):
        conn3 = sqlite3.connect("database/manufacturing.db")
        conn3.execute("DELETE FROM products WHERE source = 'example'")
        conn3.commit()
        conn3.close()
        st.success("Example products cleared.")
        st.rerun()

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