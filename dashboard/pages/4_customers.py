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
import uuid

st.subheader("➕ Add New Customer")
with st.form("add_customer_form", clear_on_submit=True):
    customer_name = st.text_input("Customer Name")
    city = st.text_input("City")
    customer_type = st.selectbox("Customer Type", ["Retail", "Wholesale", "Distributor"])
    submitted = st.form_submit_button("Add Customer")

    if submitted:
        new_id = "C-" + uuid.uuid4().hex[:6]
        conn2 = sqlite3.connect("database/manufacturing.db")
        conn2.execute(
            "INSERT INTO customers (customer_id, customer_name, city, customer_type, source) VALUES (?, ?, ?, ?, 'real')",
            (new_id, customer_name, city, customer_type)
        )
        conn2.commit()
        conn2.close()
        st.success(f"Customer '{customer_name}' added!")
        st.rerun()

with st.expander("🧹 Manage example data"):
    if st.button("Delete all example customers"):
        conn3 = sqlite3.connect("database/manufacturing.db")
        conn3.execute("DELETE FROM customers WHERE source = 'example'")
        conn3.commit()
        conn3.close()
        st.success("Example customers cleared.")
        st.rerun()

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