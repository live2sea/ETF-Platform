import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/etf.db"
)

df = pd.read_sql(
    """
    SELECT *
    FROM ods_trade_record
    LIMIT 10
    """,
    conn
)

print(df)

print()

print("总记录数：", len(
    pd.read_sql(
        "select * from ods_trade_record",
        conn
    )
))

conn.close()