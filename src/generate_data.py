
import pandas as pd
import random
from datetime import datetime, timedelta


random.seed(42)


# ==================================================
# CUSTOMERS
# ==================================================

customer_names = [
    "Apex Sports",
    "Global Sports",
    "Punjab Traders",
    "Elite Athletics",
    "North Star Sports",
    "Victory Sports",
    "Prime Athletics",
    "Urban Sports",
    "Galaxy Traders",
    "Pro Sports India",
    "Champion Traders",
    "Active Sports",
    "Royal Sports",
    "Dynamic Athletics",
    "Sports Hub",
    "Maxx Sports",
    "Super Sports",
    "United Traders",
    "Star Athletics",
    "Fit Sports",
    "Power Sports",
    "Excel Traders",
    "Olympic Sports",
    "Rapid Sports",
    "Metro Athletics",
    "National Traders",
    "SportZone",
    "TopGear Sports",
    "Future Athletics",
    "Punjab Sports House"
]

cities = [
    "Jalandhar",
    "Ludhiana",
    "Amritsar",
    "Chandigarh",
    "Delhi",
    "Mumbai",
    "Jaipur",
    "Kolkata"
]

customer_types = [
    "Retailer",
    "Wholesaler",
    "Distributor"
]


customers = pd.DataFrame({
    "customer_id": [
        f"C{i:03d}" for i in range(1, 31)
    ],

    "customer_name": customer_names,

    "city": [
        random.choice(cities)
        for _ in range(30)
    ],

    "customer_type": [
        random.choice(customer_types)
        for _ in range(30)
    ]
})


customers.to_csv(
    "data/customers.csv",
    index=False
)


# ==================================================
# PRODUCTS
# ==================================================

product_names = [
    "Football Gloves",
    "Leather Jacket",
    "Sports Shoes",
    "Cricket Bat",
    "Football",
    "Cricket Gloves",
    "Leather Wallet",
    "Sports Bag",
    "Running Shoes",
    "Football Jersey",
    "Cricket Helmet",
    "Leather Belt",
    "Training Shorts",
    "Goalkeeper Gloves",
    "Tennis Racket",
    "Sports Socks",
    "Leather Boots",
    "Basketball",
    "Basketball Jersey",
    "Gym Gloves",
    "Track Pants",
    "Leather Ball",
    "Sports Cap",
    "Hockey Stick",
    "Training T-Shirt"
]

categories = [
    "Sportswear",
    "Leather",
    "Footwear",
    "Equipment"
]


products = pd.DataFrame({
    "product_id": [
        f"P{i:03d}" for i in range(1, 26)
    ],

    "product_name": product_names,

    "category": [
        random.choice(categories)
        for _ in range(25)
    ],

    "unit_price": [
        random.randint(500, 5000)
        for _ in range(25)
    ],

    "reorder_level": [
        random.randint(10, 30)
        for _ in range(25)
    ]
})


products.to_csv(
    "data/products.csv",
    index=False
)


# ==================================================
# ORDERS
# ==================================================

start_date = datetime(2026, 1, 1)

orders_data = []


for i in range(1, 501):

    order_date = start_date + timedelta(
        days=random.randint(0, 240)
    )

    due_date = order_date + timedelta(
        days=random.randint(5, 20)
    )

    status = random.choices(
        [
            "Completed",
            "Pending",
            "Delayed",
            "Cancelled"
        ],
        weights=[55, 20, 15, 10]
    )[0]

    orders_data.append({
        "order_id": f"O{i:04d}",

        "customer_id": random.choice(
            customers["customer_id"].tolist()
        ),

        "product_id": random.choice(
            products["product_id"].tolist()
        ),

        "order_date": order_date.strftime(
            "%Y-%m-%d"
        ),

        "quantity": random.randint(1, 50),

        "due_date": due_date.strftime(
            "%Y-%m-%d"
        ),

        "status": status
    })


orders = pd.DataFrame(orders_data)


orders.to_csv(
    "data/orders.csv",
    index=False
)


# ==================================================
# PRODUCTION
# ==================================================

production_data = []


for i, order in orders.iterrows():

    order_quantity = order["quantity"]

    produced_quantity = random.randint(
        max(1, order_quantity - 5),
        order_quantity
    )

    defective_quantity = random.randint(
        0,
        max(1, int(produced_quantity * 0.10))
    )

    production_status = random.choices(
        [
            "Completed",
            "In Progress",
            "Pending"
        ],
        weights=[60, 25, 15]
    )[0]

    production_date = (
        pd.to_datetime(order["order_date"])
        + pd.Timedelta(
            days=random.randint(1, 10)
        )
    )

    production_data.append({

        "production_id":
            f"PR{i + 1:04d}",

        "order_id":
            order["order_id"],

        "production_date":
            production_date.strftime(
                "%Y-%m-%d"
            ),

        "quantity_produced":
            produced_quantity,

        "defective_quantity":
            defective_quantity,

        "production_status":
            production_status
    })


production = pd.DataFrame(
    production_data
)


production.to_csv(
    "data/production.csv",
    index=False
)


# ==================================================
# INVENTORY
# ==================================================

inventory_data = []


for i, product in products.iterrows():

    stock = random.randint(0, 60)

    inventory_data.append({

        "inventory_id":
            f"I{i + 1:03d}",

        "product_id":
            product["product_id"],

        "stock_quantity":
            stock,

        "last_updated":
            "2026-08-31"
    })


inventory = pd.DataFrame(
    inventory_data
)


inventory.to_csv(
    "data/inventory.csv",
    index=False
)


print("All datasets generated successfully!")

print(
    f"Customers: {len(customers)}"
)

print(
    f"Products: {len(products)}"
)

print(
    f"Orders: {len(orders)}"
)

print(
    f"Production records: {len(production)}"
)

print(
    f"Inventory records: {len(inventory)}"
)