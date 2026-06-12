# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/etf.db"
)

df = pd.read_sql(
    """
    SELECT *
    FROM ods_market_kline
    ORDER BY etf_code DESC
    """,
    conn
)

conn.close()

print(df)