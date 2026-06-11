import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/etf.db"
)

df = pd.read_sql(
    """
    SELECT *
    FROM dwd_profit_analysis
    ORDER BY profit_rank
    """,
    conn
)

print(df)

conn.close()