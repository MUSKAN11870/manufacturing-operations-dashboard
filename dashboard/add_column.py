import sqlite3
conn = sqlite3.connect("../database/manufacturing.db")
conn.execute("ALTER TABLE orders ADD COLUMN source TEXT DEFAULT 'example'")
conn.commit()
conn.close()
print("done")