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

st.title("📦 stock")


import uuid

st.subheader("➕ Add / Update Stock")

conn_lookup = sqlite3.connect("database/manufacturing.db")
products_list = pd.read_sql_query("SELECT product_id, product_name FROM products", conn_lookup)
conn_lookup.close()

with st.form("add_stock_form", clear_on_submit=True):
    product_choice = st.selectbox("Product", products_list["product_name"])
    stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1)
    submitted = st.form_submit_button("Save Stock Entry")

    if submitted:
        product_id = products_list[products_list["product_name"] == product_choice]["product_id"].values[0]
        new_id = "INV-" + uuid.uuid4().hex[:8]
        conn2 = sqlite3.connect("database/manufacturing.db")
        conn2.execute(
            "INSERT INTO inventory (inventory_id, product_id, stock_quantity, last_updated, source) VALUES (?, ?, ?, ?, 'real')",
            (new_id, product_id, stock_quantity, str(uuid.uuid1().time))
        )
        conn2.commit()
        conn2.close()
        st.success(f"Stock updated for {product_choice}!")
        st.rerun()

with st.expander("🧹 Manage example data"):
    confirm = st.checkbox("Yes, I'm sure I want to delete example stock entries")
    if st.button("Delete all example stock entries") and confirm:
        conn3 = sqlite3.connect("database/manufacturing.db")
        conn3.execute("DELETE FROM inventory WHERE source = 'example'")
        conn3.commit()
        conn3.close()
        st.success("Example stock entries cleared.")
        st.rerun()

st.subheader("🔍 Search Stock")
search_term = st.text_input("Search by product")

st.subheader("📊 Stock Status")

st.bar_chart(
    inventory["stock_status"].value_counts()
)

st.subheader("⚠️ Products Requiring Attention")

attention = inventory[
    inventory["stock_status"] != "Healthy Stock"
]

if search_term:
    filtered_inventory = inventory[
        inventory.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
    ]
else:
    filtered_inventory = inventory

st.dataframe(filtered_inventory, use_container_width=True, hide_index=True)

st.subheader("📋 Inventory")

st.dataframe(
    inventory,
    use_container_width=True,
    hide_index=True
)

conn.close()