# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class SignalHistoryEngine(BaseEngine):
    """信号历史查看器 — 纯查询，不做 ETL"""

    def run(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql(
            """
            SELECT trade_date, etf_code, etf_name, signal_score
            FROM dwd_signal_history
            ORDER BY trade_date DESC
            """,
            conn,
        )
        conn.close()

        print()
        print("=" * 80)
        print("历史信号记录")
        print("=" * 80)
        print(df.head(50))


if __name__ == "__main__":
    SignalHistoryEngine().run()
