import streamlit as st
import pandas as pd
import sqlite3


# ---------------- PAGE SETUP ----------------

st.set_page_config(
    page_title="Manufacturing Dashboard",
    page_icon="🏭",
    layout="wide"
)


# ---------------- DATABASE ----------------

conn = sqlite3.connect("database/manufacturing.db")


def load_table(table_name):
    return pd.read_sql_query(
        f"SELECT * FROM {table_name}",
        conn
    )


orders = load_table("orders")
customers = load_table("customers")
products = load_table("products")
inventory = load_table("inventory")
production = load_table("production")
# ---------------- PRODUCT ANALYSIS ----------------

product_analysis = pd.read_sql_query("""
    SELECT
        p.product_id,
        p.product_name,
        p.category,

        COALESCE(o.total_ordered, 0) AS units_ordered,

        COALESCE(pr.total_produced, 0) AS units_produced,

        COALESCE(pr.total_defective, 0) AS defective_units,

        CASE
            WHEN COALESCE(pr.total_produced, 0) > 0
            THEN ROUND(
                COALESCE(pr.total_defective, 0) * 100.0
                / pr.total_produced,
                2
            )
            ELSE 0
        END AS defect_rate,

        COALESCE(o.total_revenue, 0) AS revenue,

        COALESCE(i.stock_quantity, 0) AS current_stock,

        p.reorder_level,

        CASE
            WHEN COALESCE(i.stock_quantity, 0) = 0
                THEN 'Out of Stock'

            WHEN COALESCE(i.stock_quantity, 0) < p.reorder_level
                THEN 'Low Stock'

            ELSE 'Healthy Stock'
        END AS stock_status

    FROM products p

    LEFT JOIN (
        SELECT
            o.product_id,

            SUM(o.quantity) AS total_ordered,

            SUM(
                o.quantity * p.unit_price
            ) AS total_revenue

        FROM orders o

        JOIN products p
        ON o.product_id = p.product_id

        GROUP BY o.product_id

    ) o

    ON p.product_id = o.product_id

    LEFT JOIN (
        SELECT
            o.product_id,

            SUM(pr.quantity_produced)
                AS total_produced,

            SUM(pr.defective_quantity)
                AS total_defective

        FROM production pr

        JOIN orders o
        ON pr.order_id = o.order_id

        GROUP BY o.product_id

    ) pr

    ON p.product_id = pr.product_id

    LEFT JOIN inventory i

    ON p.product_id = i.product_id

    ORDER BY revenue DESC
""", conn)
# ---------------- CUSTOMER ANALYSIS ----------------

customer_analysis = pd.read_sql_query("""
    SELECT
        c.customer_id,
        c.customer_name,
        c.city,
        c.customer_type,

        COUNT(o.order_id) AS total_orders,

        COALESCE(SUM(o.quantity), 0) AS units_ordered,

        COALESCE(
            SUM(o.quantity * p.unit_price),
            0
        ) AS revenue,

        SUM(
            CASE
                WHEN LOWER(o.status) = 'pending'
                THEN 1
                ELSE 0
            END
        ) AS pending_orders,

        SUM(
            CASE
                WHEN LOWER(o.status) = 'delayed'
                THEN 1
                ELSE 0
            END
        ) AS delayed_orders

    FROM customers c

    LEFT JOIN orders o
    ON c.customer_id = o.customer_id

    LEFT JOIN products p
    ON o.product_id = p.product_id

    GROUP BY
        c.customer_id,
        c.customer_name,
        c.city,
        c.customer_type

    ORDER BY revenue DESC
""", conn)

# Calculate revenue in a numeric format
product_analysis["revenue"] = product_analysis[
    "revenue"
].round(2)

# ==================================================
# CUSTOMER ANALYSIS
# ==================================================

st.subheader("👥 Customer Analysis")

st.dataframe(
    customer_analysis,
    use_container_width=True,
    hide_index=True
)
st.write("### 🏆 Top 5 Customers by Revenue")

top_customers = (
    customer_analysis[
        ["customer_name", "revenue"]
    ]
    .head(5)
    .set_index("customer_name")
)

st.bar_chart(top_customers)
st.write("### ⚠️ Customers with Delayed Orders")

customers_attention = customer_analysis[
    customer_analysis["delayed_orders"] > 0
]

if len(customers_attention) == 0:

    st.success(
        "✅ No customers currently have delayed orders."
    )

else:

    st.dataframe(
        customers_attention[
            [
                "customer_name",
                "city",
                "customer_type",
                "total_orders",
                "delayed_orders",
                "revenue"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

 # ==================================================
# INVENTORY INTELLIGENCE
# ==================================================
# ---------------- INVENTORY ANALYSIS ----------------

inventory_analysis = pd.read_sql_query("""
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        i.stock_quantity,
        p.reorder_level,

        CASE
            WHEN i.stock_quantity = 0
                THEN 'Out of Stock'

            WHEN i.stock_quantity < p.reorder_level
                THEN 'Low Stock'

            ELSE 'Healthy Stock'
        END AS stock_status,

        ROUND(
            i.stock_quantity * p.unit_price,
            2
        ) AS inventory_value

    FROM products p

    LEFT JOIN inventory i
    ON p.product_id = i.product_id

    ORDER BY stock_quantity ASC
""", conn)
st.subheader("📦 Inventory Intelligence")

st.dataframe(
    inventory_analysis,
    use_container_width=True,
    hide_index=True
)   
st.write("### 📊 Inventory Status")

inventory_status = (
    inventory_analysis["stock_status"]
    .value_counts()
)

st.bar_chart(inventory_status)
# ---------------- PREPARE DATES ----------------

orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["due_date"] = pd.to_datetime(orders["due_date"])

production["production_date"] = pd.to_datetime(
    production["production_date"]
)


# ---------------- TITLE ----------------

st.title("🏭 Manufacturing Operations Dashboard")

st.write(
    "Monitor orders, production, inventory and customer activity."
)


# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("🔎 Filters")


# Order status filter

status_options = ["All"] + sorted(
    orders["status"].dropna().unique().tolist()
)

selected_status = st.sidebar.selectbox(
    "Order Status",
    status_options
)


# Product filter

product_options = ["All"] + sorted(
    orders["product_id"].dropna().unique().tolist()
)

selected_product = st.sidebar.selectbox(
    "Product",
    product_options
)


# Date filter

st.sidebar.subheader("📅 Date Filter")

min_date = orders["order_date"].min().date()
max_date = orders["order_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date)
)


# ==================================================
# APPLY FILTERS
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

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

    filtered_orders = filtered_orders[
        (filtered_orders["order_date"] >= start_date)
        &
        (filtered_orders["order_date"] <= end_date)
    ]


# ==================================================
# KPI SECTION
# ==================================================

st.subheader("📊 Operations Overview")


total_orders = len(filtered_orders)

completed_orders = len(
    filtered_orders[
        filtered_orders["status"].str.lower() == "completed"
    ]
)

pending_orders = len(
    filtered_orders[
        filtered_orders["status"].str.lower() == "pending"
    ]
)

delayed_orders = len(
    filtered_orders[
        filtered_orders["status"].str.lower() == "delayed"
    ]
)

low_stock_products = len(
    inventory[
        inventory["stock_quantity"] <= 10
    ]
)
# ---------------- REVENUE ANALYTICS ----------------

revenue_data = orders.merge(
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

if total_orders > 0:
    average_order_value = (
        total_revenue / total_orders
    )
else:
    average_order_value = 0



col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col1:
    st.metric("Total Orders", total_orders)


with col2:
    st.metric("Completed", completed_orders)


with col3:
    st.metric("Pending", pending_orders)


with col4:
    st.metric("Delayed", delayed_orders)


with col5:
    st.metric("Low Stock", low_stock_products)

with col6:
    st.metric(
        "Total Revenue",
        f"₹{total_revenue:,.0f}"
    )

with col7:
    st.metric(
        "Avg Order Value",
        f"₹{average_order_value:,.0f}"
    )


# ==================================================
# ALERTS
# ==================================================

st.subheader("🚨 Alerts")


# Low stock

low_stock = inventory[
    inventory["stock_quantity"] <= 10
]


# Delayed

delayed = orders[
    orders["status"].str.lower() == "delayed"
]


# Pending

pending = orders[
    orders["status"].str.lower() == "pending"
]


# Due soon

today = pd.Timestamp.today().normalize()

due_soon = orders[
    (orders["due_date"] >= today)
    &
    (orders["due_date"] <= today + pd.Timedelta(days=3))
    &
    (orders["status"].str.lower() != "completed")
]


if len(low_stock) == 0:
    st.success("✅ No low-stock products.")

else:
    st.warning(
        f"⚠️ {len(low_stock)} product(s) have low stock."
    )


if len(delayed) == 0:
    st.success("✅ No delayed orders.")

else:
    st.error(
        f"🔴 {len(delayed)} order(s) are delayed."
    )


if len(pending) == 0:
    st.success("✅ No pending orders.")

else:
    st.info(
        f"🟡 {len(pending)} order(s) are pending."
    )


if len(due_soon) > 0:
    st.warning(
        f"⏰ {len(due_soon)} order(s) are due within 3 days."
    )


# ==================================================
# PRODUCTION PERFORMANCE
# ==================================================

st.subheader("🏭 Production Performance")


total_produced = int(
    production["quantity_produced"].sum()
)

total_defective = int(
    production["defective_quantity"].sum()
)


if total_produced > 0:

    defect_rate = (
        total_defective / total_produced
    ) * 100

else:

    defect_rate = 0


production_completed = len(
    production[
        production["production_status"].str.lower()
        == "completed"
    ]
)


pcol1, pcol2, pcol3, pcol4 = st.columns(4)


with pcol1:
    st.metric(
        "Total Produced",
        total_produced
    )


with pcol2:
    st.metric(
        "Defective Units",
        total_defective
    )


with pcol3:
    st.metric(
        "Defect Rate",
        f"{defect_rate:.2f}%"
    )


with pcol4:
    st.metric(
        "Completed Production",
        production_completed
    )


# ==================================================
# CHARTS
# ==================================================

st.subheader("📈 Analytics")


chart1, chart2 = st.columns(2)


# Order status chart

with chart1:

    st.write("### Orders by Status")

    status_chart = (
        orders["status"]
        .value_counts()
    )

    st.bar_chart(status_chart)


# Inventory chart

with chart2:

    st.write("### Inventory Levels")

    inventory_chart = inventory[
        ["product_id", "stock_quantity"]
    ].set_index("product_id")

    st.bar_chart(inventory_chart)


# Production chart

st.write("### Production Over Time")

production_chart = (
    production
    .groupby("production_date")["quantity_produced"]
    .sum()
)

st.line_chart(production_chart)
st.write("### 💰 Revenue Over Time")

revenue_time = (
    revenue_data
    .groupby("order_date")["revenue"]
    .sum()
)

st.line_chart(revenue_time)


st.write("### 🏆 Top 5 Products by Revenue")

top_products = (
    revenue_data
    .groupby("product_id")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

st.bar_chart(top_products)
st.write("### 📊 Revenue by Category")

category_revenue = (
    revenue_data
    .merge(
        products[
            ["product_id", "category"]
        ],
        on="product_id",
        how="left"
    )
    .groupby("category")["revenue"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(category_revenue)

# ==================================================
# ORDERS REQUIRING ATTENTION
# ==================================================

st.subheader("⚠️ Orders Requiring Attention")


attention_orders = orders[
    orders["status"].str.lower().isin(
        ["pending", "delayed"]
    )
].copy()


if len(attention_orders) == 0:

    st.success("✅ No orders currently require attention.")

else:

    st.dataframe(
        attention_orders[
            [
                "order_id",
                "customer_id",
                "product_id",
                "due_date",
                "quantity",
                "status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )
# ==================================================
# PRODUCT ANALYSIS
# ==================================================

st.subheader("📊 Product-wise Analysis")

st.dataframe(
    product_analysis,
    use_container_width=True,
    hide_index=True
)
st.write("### 💰 Revenue by Product")

revenue_chart = (
    product_analysis[
        ["product_name", "revenue"]
    ]
    .set_index("product_name")
    .sort_values("revenue", ascending=False)
)

st.bar_chart(revenue_chart)


st.write("### ⚠️ Products with Stock Issues")

stock_issues = product_analysis[
    product_analysis["stock_status"] != "Healthy Stock"
]

if len(stock_issues) == 0:

    st.success(
        "✅ All products have healthy stock levels."
    )

else:

    st.dataframe(
        stock_issues[
            [
                "product_id",
                "product_name",
                "category",
                "current_stock",
                "reorder_level",
                "stock_status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )
# ==================================================
# ORDERS
# ==================================================

st.subheader("📦 Orders")

st.dataframe(
    filtered_orders,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# INVENTORY
# ==================================================

st.subheader("📦 Inventory")

st.dataframe(
    inventory,
    use_container_width=True,
    hide_index=True
)
# ---------------- PRODUCTION ANALYSIS ----------------

production_analysis = pd.read_sql_query("""
    SELECT
        p.product_id,
        p.product_name,

        SUM(pr.quantity_produced) AS units_produced,

        SUM(pr.defective_quantity) AS defective_units,

        ROUND(
            SUM(pr.defective_quantity) * 100.0
            / NULLIF(SUM(pr.quantity_produced), 0),
            2
        ) AS defect_rate

    FROM production pr

    JOIN orders o
    ON pr.order_id = o.order_id

    JOIN products p
    ON o.product_id = p.product_id

    GROUP BY
        p.product_id,
        p.product_name

    ORDER BY defect_rate DESC
""", conn)


# ==================================================
# PRODUCTION
# ==================================================

st.subheader("🏭 Production")

st.dataframe(
    production,
    use_container_width=True,
    hide_index=True
)
st.subheader("🏭 Production Intelligence")

st.dataframe(
    production_analysis,
    use_container_width=True,
    hide_index=True
)

st.write("### ⚠️ Defects by Product")

defect_chart = (
    production_analysis[
        ["product_name", "defective_units"]
    ]
    .set_index("product_name")
    .sort_values(
        "defective_units",
        ascending=False
    )
)

st.bar_chart(defect_chart)

st.write("### 🔴 Highest Defect Products")

high_defect = production_analysis[
    production_analysis["defect_rate"] >= 5
]

if len(high_defect) == 0:

    st.success(
        "✅ No products have a defect rate of 5% or higher."
    )

else:

    st.dataframe(
        high_defect[
            [
                "product_id",
                "product_name",
                "units_produced",
                "defective_units",
                "defect_rate"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Manufacturing Operations Dashboard • "
    "Python • Pandas • SQLite • Streamlit"
)


conn.close()