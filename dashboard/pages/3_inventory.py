import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Inventory", page_icon="📦", layout="wide")

conn = sqlite3.connect("database/manufacturing.db")

inventory = pd.read_sql_query(
    "SELECT * FROM inventory",
    conn
)

products = pd.read_sql_query(
    "SELECT * FROM products",
    conn
)

inventory = inventory.merge(
    products[
        ["product_id", "product_name", "reorder_level"]
    ],
    on="product_id",
    how="left"
)

inventory["stock_status"] = inventory.apply(
    lambda row:
        "Out of Stock"
        if row["stock_quantity"] == 0
        else "Low Stock"
        if row["stock_quantity"] < row["reorder_level"]
        else "Healthy Stock",
    axis=1
)

st.title("📦 Inventory")

st.subheader("📊 Stock Status")

st.bar_chart(
    inventory["stock_status"].value_counts()
)

st.subheader("⚠️ Products Requiring Attention")

attention = inventory[
    inventory["stock_status"] != "Healthy Stock"
]

st.dataframe(
    attention,
    use_container_width=True,
    hide_index=True
)

st.subheader("📋 Inventory")

st.dataframe(
    inventory,
    use_container_width=True,
    hide_index=True
)

conn.close()