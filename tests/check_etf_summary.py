import sqlite3
import pandas as pd

conn = sqlite3.connect("data/etf.db")

df = pd.read_sql("""
SELECT

    etf_code,
    etf_name,

    COUNT(*) AS trade_count,

    SUM(
        CASE
            WHEN trade_type='买入'
            THEN quantity
            ELSE 0
        END
    ) AS buy_qty,

    SUM(
        CASE
            WHEN trade_type='卖出'
            THEN quantity
            ELSE 0
        END
    ) AS sell_qty

FROM ods_trade_record

GROUP BY
    etf_code,
    etf_name

ORDER BY trade_count DESC
""", conn)

print(df)

conn.close()