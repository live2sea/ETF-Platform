import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/etf.db"
)

df = pd.read_sql(
    """
    SELECT *
    FROM dwd_position
    ORDER BY quantity DESC
    """,
    conn
)

print(df)

conn.close()