import sqlite3
import pandas as pd
connection = sqlite3.connect("database/manufacturing.db")
customers = pd.read_csv("data/customers.csv")
customers.to_sql(
    "customers",
    connection,
    if_exists="replace",
    index=False
)

products = pd.read_csv("data/products.csv")
products.to_sql(
    "products",
    connection,
    if_exists="replace",
    index=False
)

orders = pd.read_csv("data/orders.csv")
orders.to_sql(
    "orders",
    connection,
    if_exists="replace",
    index=False
)

production = pd.read_csv("data/production.csv")
production.to_sql(
    "production",
    connection,
    if_exists="replace",
    index=False
)

inventory = pd.read_csv("data/inventory.csv")
inventory.to_sql(
    "inventory",
    connection,
    if_exists="replace",
    index=False
)

connection.close()

print("Database created successfully!")