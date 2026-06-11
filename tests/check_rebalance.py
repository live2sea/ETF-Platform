# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/etf.db"
)

df = pd.read_sql(
    """
    SELECT *
    FROM dwd_rebalance
    ORDER BY deviation_pct DESC
    """,
    conn
)

conn.close()

print(df)