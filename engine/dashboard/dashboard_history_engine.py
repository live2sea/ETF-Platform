# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class DashboardHistoryEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):

        conn = sqlite3.connect(self.db_path)

        self.dashboard_df = pd.read_sql(
            """
            SELECT *
            FROM dwd_dashboard
            """,
            conn
        )

        conn.close()

    def transform(self):

        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        def get_value(item_name):

            row = self.dashboard_df[
                self.dashboard_df["item_name"] == item_name
            ]

            if row.empty:
                return None

            return row.iloc[0]["item_value"]

        total_cost = float(get_value("总成本") or 0)

        total_market = float(get_value("总市值") or 0)

        total_profit = float(get_value("总盈亏") or 0)

        profit_pct = (
            str(get_value("收益率") or "0")
            .replace("%", "")
        )

        profit_pct = float(profit_pct)

        best_etf = get_value("最佳ETF")

        recommend_etf = get_value("推荐加仓")

        risk_count = int(
            get_value("高风险项数量") or 0
        )

        self.result_df = pd.DataFrame(
            [[
                today,
                total_cost,
                total_market,
                total_profit,
                profit_pct,
                best_etf,
                recommend_etf,
                risk_count,
                now
            ]],
            columns=[
                "trade_date",
                "total_cost",
                "total_market",
                "total_profit",
                "profit_pct",
                "best_etf",
                "recommend_etf",
                "risk_count",
                "update_time"
            ]
        )

    def load(self):

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            """
            DELETE FROM dwd_dashboard_history
            WHERE trade_date=?
            """,
            (
                self.result_df.iloc[0]["trade_date"],
            )
        )

        self.result_df.to_sql(
            "dwd_dashboard_history",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()
        conn.close()

    def print_result(self):

        print()
        print("=" * 100)
        print("Dashboard历史快照")
        print("=" * 100)

        print(self.result_df)

    def run(self):

        super().run()
        self.print_result()


if __name__ == "__main__":
    DashboardHistoryEngine().run()