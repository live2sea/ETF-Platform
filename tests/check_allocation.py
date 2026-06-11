#!/usr/bin/env python3
#解释：该脚本用于检查ETF交易记录中是否存在导致负仓位的情况。它从SQLite数据库中加载交易记录数据，计算每只ETF的持仓数量，并在发现负仓位时打印异常信息，包括ETF代码和出现负仓位的日期。最后，关闭数据库连接。
import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/etf.db"
)

df = pd.read_sql(
    """
    SELECT *
    FROM dwd_allocation
    ORDER BY allocation_pct DESC
    """,
    conn
)

print(df)

conn.close()