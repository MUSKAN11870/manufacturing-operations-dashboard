import streamlit as st
import pandas as pd
import sqlite3


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Manufacturing Operations",
    page_icon="🏭",
    layout="wide"
)
st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1 {
    font-size: 2.4rem;
    font-weight: 700;
}

h2, h3 {
    margin-top: 1.5rem;
}

[data-testid="stMetric"] {
    background-color: rgba(128, 128, 128, 0.08);
    padding: 15px;
    border-radius: 10px;
    border: 1px solid rgba(128, 128, 128, 0.15);
}

[data-testid="stMetricValue"] {
    font-size: 1.7rem;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# DATABASE CONNECTION
# ==================================================

conn = sqlite3.connect(
    "database/manufacturing.db"
)


def load_table(table_name):
    return pd.read_sql_query(
        f"SELECT * FROM {table_name}",
        conn
    )


# ==================================================
# LOAD DATA
# ==================================================

orders = load_table("orders")
products = load_table("products")
inventory = load_table("inventory")
production = load_table("production")


orders["order_date"] = pd.to_datetime(
    orders["order_date"]
)

orders["due_date"] = pd.to_datetime(
    orders["due_date"]
)

production["production_date"] = pd.to_datetime(
    production["production_date"]
)


# ==================================================
# TITLE
# ==================================================

st.title("🏭 Manufacturing Operations Dashboard")

st.write(
    "Monitor orders, revenue, production and inventory "
    "from one place."
)


# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("🔎 Filters")


status_options = ["All"] + sorted(
    orders["status"].dropna().unique().tolist()
)

selected_status = st.sidebar.selectbox(
    "Order Status",
    status_options
)


product_options = ["All"] + sorted(
    products["product_id"].dropna().unique().tolist()
)

selected_product = st.sidebar.selectbox(
    "Product",
    product_options
)


# ==================================================
# DATE FILTER
# ==================================================

min_date = orders["order_date"].min().date()
max_date = orders["order_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date)
)


# ==================================================
# FILTER ORDERS
# ==================================================

filtered_orders = orders.copy()


if selected_status != "All":

    filtered_orders = filtered_orders[
        filtered_orders["status"] == selected_status
    ]


if selected_product != "All":

    filtered_orders = filtered_orders[
        filtered_orders["product_id"] == selected_product
    ]


if len(selected_dates) == 2:

    start_date = pd.Timestamp(
        selected_dates[0]
    )

    end_date = pd.Timestamp(
        selected_dates[1]
    )

    filtered_orders = filtered_orders[
        (filtered_orders["order_date"] >= start_date)
        &
        (filtered_orders["order_date"] <= end_date)
    ]


# ==================================================
# REVENUE
# ==================================================

revenue_data = filtered_orders.merge(
    products[
        ["product_id", "unit_price"]
    ],
    on="product_id",
    how="left"
)


revenue_data["revenue"] = (
    revenue_data["quantity"]
    * revenue_data["unit_price"]
)


total_revenue = revenue_data["revenue"].sum()


# ==================================================
# KPI CALCULATIONS
# ==================================================

total_orders = len(filtered_orders)


completed_orders = len(
    filtered_orders[
        filtered_orders["status"].str.lower()
        == "completed"
    ]
)


pending_orders = len(
    filtered_orders[
        filtered_orders["status"].str.lower()
        == "pending"
    ]
)


delayed_orders = len(
    filtered_orders[
        filtered_orders["status"].str.lower()
        == "delayed"
    ]
)


low_stock_products = len(
    inventory.merge(
        products[
            ["product_id", "reorder_level"]
        ],
        on="product_id",
        how="left"
    ).query(
        "stock_quantity < reorder_level"
    )
)


# ==================================================
# KPI CARDS
# ==================================================

st.subheader("📊 Business Overview")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Orders",
        total_orders
    )


with col2:
    if total_revenue >= 100000:
        revenue_display = f"₹{total_revenue / 100000:.1f}L"
    else:
        revenue_display = f"₹{total_revenue:,.0f}"

    st.metric(
        "Revenue",
        revenue_display
    )


with col3:

    st.metric(
        "Completed",
        completed_orders
    )


with col4:

    st.metric(
        "Delayed",
        delayed_orders
    )


    st.metric(
    "Low Stock",
    low_stock_products
)




# ==================================================
# ALERTS
# ==================================================

st.subheader("🚨 Critical Alerts")


alerts_found = False


if delayed_orders > 0:

    st.error(
        f"🔴 {delayed_orders} delayed order(s) "
        "require attention."
    )

    alerts_found = True


if pending_orders > 0:

    st.warning(
        f"🟡 {pending_orders} pending order(s)."
    )

    alerts_found = True


if low_stock_products > 0:

    st.warning(
        f"📦 {low_stock_products} product(s) "
        "are below reorder level."
    )

    alerts_found = True


if not alerts_found:

    st.success(
        "✅ No critical operational issues detected."
    )


# ==================================================
# DASHBOARD CHARTS
# ==================================================

st.subheader("📈 Operations Overview")


chart1, chart2 = st.columns(2)


# ---------------- ORDERS ----------------

with chart1:

    st.write("### Orders by Status")

    status_chart = (
        filtered_orders["status"]
        .value_counts()
    )

    st.bar_chart(status_chart)


# ---------------- REVENUE ----------------

with chart2:

    st.write("### Revenue by Product")

    revenue_chart = (
        revenue_data
        .groupby("product_id")["revenue"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    st.bar_chart(revenue_chart)






# ==================================================
# LOW STOCK PRODUCTS
# ==================================================

st.subheader("📦 Stock Requiring Attention")


inventory_check = inventory.merge(
    products[
        [
            "product_id",
            "product_name",
            "reorder_level"
        ]
    ],
    on="product_id",
    how="left"
)


inventory_check["stock_status"] = inventory_check.apply(
    lambda row:
        "Out of Stock"
        if row["stock_quantity"] == 0
        else
        "Low Stock"
        if row["stock_quantity"] < row["reorder_level"]
        else
        "Healthy Stock",
    axis=1
)


inventory_attention = inventory_check[
    inventory_check["stock_status"] != "Healthy Stock"
]


if len(inventory_attention) == 0:

    st.success(
        "✅ No stock issues."
    )

else:

    st.dataframe(
        inventory_attention[
            [
                "product_id",
                "product_name",
                "stock_quantity",
                "reorder_level",
                "stock_status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# ORDERS REQUIRING ATTENTION
# ==================================================


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Manufacturing Operations Analytics • "
    "Python • Pandas • SQL • SQLite • Streamlit"
)


conn.close()