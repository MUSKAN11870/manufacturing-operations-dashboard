import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Production", page_icon="🏭", layout="wide")

conn = sqlite3.connect("database/manufacturing.db")

production = pd.read_sql_query(
    "SELECT * FROM production",
    conn
)

st.title("🏭 Production")
import uuid

st.subheader("➕ Add New Production Entry")

conn_lookup = sqlite3.connect("database/manufacturing.db")
orders_list = pd.read_sql_query("SELECT order_id FROM orders", conn_lookup)
conn_lookup.close()

with st.form("add_production_form", clear_on_submit=True):
    order_choice = st.selectbox("Order ID", orders_list["order_id"])
    production_date = st.date_input("Production Date")
    quantity_produced = st.number_input("Quantity Produced", min_value=0, step=1)
    defective_quantity = st.number_input("Defective Quantity", min_value=0, step=1)
    production_status = st.selectbox("Status", ["Completed", "In Progress", "Delayed"])
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        new_id = "PRD-" + uuid.uuid4().hex[:8]
        conn2 = sqlite3.connect("database/manufacturing.db")
        conn2.execute(
            "INSERT INTO production (production_id, order_id, production_date, quantity_produced, defective_quantity, production_status, source) VALUES (?, ?, ?, ?, ?, ?, 'real')",
            (new_id, order_choice, str(production_date), quantity_produced, defective_quantity, production_status)
        )
        conn2.commit()
        conn2.close()
        st.success(f"Production entry {new_id} added!")
        st.rerun()

with st.expander("🧹 Manage example data"):
    confirm = st.checkbox("Yes, I'm sure I want to delete example production entries")
    if st.button("Delete all example production entries") and confirm:
        conn3 = sqlite3.connect("database/manufacturing.db")
        conn3.execute("DELETE FROM production WHERE source = 'example'")
        conn3.commit()
        conn3.close()
        st.success("Example production entries cleared.")
        st.rerun()

st.subheader("🔍 Search Production")
search_term = st.text_input("Search by order or status")
total_produced = production["quantity_produced"].sum()
total_defects = production["defective_quantity"].sum()

defect_rate = (
    total_defects / total_produced * 100
    if total_produced > 0 else 0
)

c1, c2, c3 = st.columns(3)

c1.metric("Units Produced", f"{total_produced:,}")
c2.metric("Defective Units", f"{total_defects:,}")
c3.metric("Defect Rate", f"{defect_rate:.2f}%")

st.subheader("📈 Production Over Time")

production["production_date"] = pd.to_datetime(
    production["production_date"]
)

trend = production.groupby(
    "production_date"
)["quantity_produced"].sum()

st.line_chart(trend)

st.subheader("📋 Production Records")

if search_term:
    filtered_production = production[
        production.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
    ]
else:
    filtered_production = production

st.dataframe(filtered_production, use_container_width=True, hide_index=True)

conn.close()