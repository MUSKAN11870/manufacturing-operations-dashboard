import sqlite3
conn = sqlite3.connect("../database/manufacturing.db")
try:
    conn.execute("ALTER TABLE production ADD COLUMN source TEXT DEFAULT 'example'")
except Exception as e:
    print("production:", e)
try:
    conn.execute("ALTER TABLE inventory ADD COLUMN source TEXT DEFAULT 'example'")
except Exception as e:
    print("inventory:", e)
conn.commit()
conn.close()
print("done")