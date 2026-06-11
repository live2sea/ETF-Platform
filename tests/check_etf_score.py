import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/etf.db"
)

df = pd.read_sql("""

select *
from dwd_etf_score
order by total_score desc

""", conn)

print(df)

conn.close()