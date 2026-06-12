import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/etf.db"
)

df = pd.read_sql(
    """
    SELECT *
    FROM dwd_rsi_factor
    ORDER BY etf_code
    """,
    conn
)

print(df)

conn.close()