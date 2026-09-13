import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Orders", page_icon="📦", layout="wide")

conn = sqlite3.connect("database/manufacturing.db")

orders = pd.read_sql_query("SELECT * FROM orders", conn)

orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["due_date"] = pd.to_datetime(orders["due_date"])

st.title("📦 Orders")
st.subheader("🔍 Search Orders")
search_term = st.text_input("Search by customer, product, or status")
import uuid

st.subheader("➕ Add New Order")

conn_lookup = sqlite3.connect("database/manufacturing.db")
customers_list = pd.read_sql_query("SELECT customer_id, customer_name FROM customers", conn_lookup)
products_list = pd.read_sql_query("SELECT product_id, product_name FROM products", conn_lookup)
conn_lookup.close()

with st.form("add_order_form", clear_on_submit=True):
    customer_choice = st.selectbox("Customer", customers_list["customer_name"])
    product_choice = st.selectbox("Product", products_list["product_name"])
    order_date = st.date_input("Order Date")
    due_date = st.date_input("Due Date")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    status = st.selectbox("Status", ["Pending", "In Progress", "Completed", "Delayed"])
    submitted = st.form_submit_button("Add Order")

    if submitted:
        customer_id = customers_list[customers_list["customer_name"] == customer_choice]["customer_id"].values[0]
        product_id = products_list[products_list["product_name"] == product_choice]["product_id"].values[0]
        new_id = "ORD-" + uuid.uuid4().hex[:8]
        conn2 = sqlite3.connect("database/manufacturing.db")
        conn2.execute(
            "INSERT INTO orders (order_id, customer_id, product_id, order_date, quantity, due_date, status, source) VALUES (?, ?, ?, ?, ?, ?, ?, 'real')",
            (new_id, customer_id, product_id, str(order_date), quantity, str(due_date), status)
        )
        conn2.commit()
        conn2.close()
        st.success(f"Order {new_id} added for {customer_choice} - {product_choice}!")
        st.rerun()

with st.expander("🧹 Manage example data"):
    confirm = st.checkbox("Yes, I'm sure I want to delete example orders")
    if st.button("Delete all example orders") and confirm:
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

if search_term:
    filtered_orders = orders[
        orders.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
    ]
else:
    filtered_orders = orders

st.dataframe(
    filtered_orders,
    use_container_width=True,
    hide_index=True
)

conn.close()