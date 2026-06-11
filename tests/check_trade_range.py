import sqlite3
import pandas as pd

conn = sqlite3.connect("data/etf.db")

df = pd.read_sql("""
SELECT
    MIN(trade_date) AS first_trade_date,
    MAX(trade_date) AS last_trade_date,
    COUNT(*) AS total_records
FROM ods_trade_record
""", conn)

print("\n===== 交易记录范围 =====")
print(df)

conn.close()