# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd

from datetime import datetime

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
)

from engine.base_engine import BaseEngine


class PortfolioNavEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):

        conn = sqlite3.connect(self.db_path)

        self.profit_df = pd.read_sql(
            """
            SELECT *
            FROM dwd_floating_profit
            """,
            conn
        )

        conn.close()

    def transform(self):

        now = datetime.now()

        trade_date = now.strftime("%Y-%m-%d")

        total_cost = round(
            self.profit_df["cost_value"].sum(),
            2
        )

        total_market = round(
            self.profit_df["market_value"].sum(),
            2
        )

        total_profit = round(
            self.profit_df["floating_profit"].sum(),
            2
        )

        profit_pct = round(
            total_profit / total_cost * 100,
            2
        ) if total_cost > 0 else 0

        self.result_df = pd.DataFrame(
            [[
                trade_date,
                total_cost,
                total_market,
                total_profit,
                profit_pct,
                now.strftime("%Y-%m-%d %H:%M:%S")
            ]],
            columns=[
                "trade_date",
                "total_cost",
                "total_market",
                "total_profit",
                "profit_pct",
                "update_time"
            ]
        )

    def load(self):

        conn = sqlite3.connect(self.db_path)

        trade_date = self.result_df.iloc[0]["trade_date"]

        conn.execute(
            """
            DELETE FROM dwd_portfolio_nav_history
            WHERE trade_date=?
            """,
            [trade_date]
        )

        self.result_df.to_sql(
            "dwd_portfolio_nav_history",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()
        conn.close()

    def print_result(self):

        print()
        print("=" * 100)
        print("账户净值历史")
        print("=" * 100)

        print(self.result_df)

    def run(self):

        super().run()

        self.print_result()


if __name__ == "__main__":

    PortfolioNavEngine().run()
