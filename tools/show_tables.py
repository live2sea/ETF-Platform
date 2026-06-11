import sqlite3

conn = sqlite3.connect("data/etf.db")

tables = conn.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name
""").fetchall()

for table in tables:

    table_name = table[0]

    print("\n" + "=" * 50)
    print(table_name)

    cols = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    for col in cols:
        print(col)

conn.close()