import sqlite3
conn = sqlite3.connect("../database/manufacturing.db")
try:
    conn.execute("ALTER TABLE products ADD COLUMN source TEXT DEFAULT 'example'")
except Exception as e:
    print("products:", e)
conn.commit()
conn.close()
print("done")