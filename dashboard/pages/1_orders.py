import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Orders", page_icon="📦", layout="wide")

conn = sqlite3.connect("database/manufacturing.db")

orders = pd.read_sql_query("SELECT * FROM orders", conn)

orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["due_date"] = pd.to_datetime(orders["due_date"])

st.title("📦 Orders")
import uuid

st.subheader("➕ Add New Order")
with st.form("add_order_form", clear_on_submit=True):
    customer_id = st.text_input("Customer ID")
    product_id = st.text_input("Product ID")
    order_date = st.date_input("Order Date")
    due_date = st.date_input("Due Date")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    status = st.selectbox("Status", ["Pending", "In Progress", "Completed", "Delayed"])
    submitted = st.form_submit_button("Add Order")

    if submitted:
        new_id = "ORD-" + uuid.uuid4().hex[:8]
        conn2 = sqlite3.connect("database/manufacturing.db")
        conn2.execute(
            "INSERT INTO orders (order_id, customer_id, product_id, order_date, quantity, due_date, status, source) VALUES (?, ?, ?, ?, ?, ?, ?, 'real')",
            (new_id, customer_id, product_id, str(order_date), quantity, str(due_date), status)
        )
        conn2.commit()
        conn2.close()
        st.success(f"Order {new_id} added!")
        st.rerun()

with st.expander("🧹 Manage example data"):
    if st.button("Delete all example orders"):
        conn3 = sqlite3.connect("database/manufacturing.db")
        conn3.execute("DELETE FROM orders WHERE source = 'example'")
        conn3.commit()
        conn3.close()
        st.success("Example orders cleared.")
        st.rerun()

st.metric("Total Orders", len(orders))

st.subheader("📊 Orders by Status")
st.bar_chart(orders["status"].value_counts())

st.subheader("⚠️ Pending & Delayed Orders")

attention = orders[
    orders["status"].str.lower().isin(["pending", "delayed"])
]

st.dataframe(
    attention,
    use_container_width=True,
    hide_index=True
)

st.subheader("📋 All Orders")

st.dataframe(
    orders,
    use_container_width=True,
    hide_index=True
)

conn.close()