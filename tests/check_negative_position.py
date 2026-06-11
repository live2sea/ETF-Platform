# !/usr/bin/env python3
# 解释：该脚本用于检查ETF交易记录中是否存在导致负仓位 
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/etf.db")

df = pd.read_sql("""
SELECT *
FROM ods_trade_record
ORDER BY trade_date,trade_time
""", conn)

conn.close()

positions = {}

for _, row in df.iterrows():

    code = row["etf_code"]

    positions.setdefault(code, 0)

    if row["trade_type"] == "买入":

        positions[code] += row["quantity"]

    else:

        positions[code] -= row["quantity"]

        if positions[code] < 0:

            print(
                f"异常：{code}"
                f" 在 {row['trade_date']}"
                f" 出现负仓位"
            )