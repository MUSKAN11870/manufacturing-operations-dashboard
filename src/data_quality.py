import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "database/manufacturing.db"
)

tables = [
    "customers",
    "products",
    "orders",
    "production",
    "inventory"
]

print("========== DATA QUALITY REPORT ==========")

for table in tables:

    df = pd.read_sql_query(
        f"SELECT * FROM {table}",
        conn
    )

    print(f"\nTable: {table}")
    print(f"Rows: {len(df)}")
    print(
        f"Duplicate rows: {df.duplicated().sum()}"
    )
    print(
        f"Missing values: {df.isnull().sum().sum()}"
    )

conn.close()

print("\n========== CHECK COMPLETE ==========")