# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd


class SignalHistoryEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    def run(self):

        conn = sqlite3.connect(
            self.db_path
        )

        df = pd.read_sql(
            """
            SELECT
                trade_date,
                etf_code,
                etf_name,
                signal_score
            FROM dwd_signal_history
            ORDER BY trade_date DESC
            """,
            conn
        )

        conn.close()

        print()
        print("=" * 80)
        print("历史信号记录")
        print("=" * 80)

        print(df.head(50))


if __name__ == "__main__":

    SignalHistoryEngine().run()