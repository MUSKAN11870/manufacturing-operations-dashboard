import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Orders", page_icon="📦", layout="wide")

conn = sqlite3.connect("database/manufacturing.db")

orders = pd.read_sql_query("SELECT * FROM orders", conn)

orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["due_date"] = pd.to_datetime(orders["due_date"])

st.title("📦 Orders")

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