import sqlite3

conn = sqlite3.connect(
    "data/etf.db"
)

cursor = conn.cursor()

tables = [
    "ods_trade_record",
    "dwd_position",
    "dwd_profit_analysis",
    "dwd_allocation"
]

for table in tables:

    print()
    print("=" * 50)
    print(table)

    cursor.execute(
        f"PRAGMA table_info({table})"
    )

    for row in cursor.fetchall():

        print(row)

conn.close()