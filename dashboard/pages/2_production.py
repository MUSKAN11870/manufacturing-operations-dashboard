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

st.dataframe(
    production,
    use_container_width=True,
    hide_index=True
)

conn.close()