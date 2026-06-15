#!/usr/bin/env python3
# 解释：该脚本定义了一个ProfitEngine类，用于计算ETF的盈亏情况。
# 它从SQLite数据库中加载当前持仓数据，计算每只ETF的盈亏金额和排名，并将结果保存到数据库中的盈亏分析表中。
# 最后，在主程序中创建一个ProfitEngine实例，执行计算并打印盈亏排行榜和TOP3盈亏贡献。

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class ProfitEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 从 dwd_position 加载当前持仓"""
        conn = sqlite3.connect(self.db_path)
        self.position_df = pd.read_sql(
            """
            SELECT *
            FROM dwd_position
            """,
            conn,
        )
        conn.close()

    def transform(self):
        """Transform: 按已实现盈亏排序，生成排名"""
        df = self.position_df

        df = df.sort_values(by="realized_profit", ascending=False)

        df["profit_rank"] = range(1, len(df) + 1)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df["update_time"] = now

        self.result_df = df[
            [
                "etf_code",
                "etf_name",
                "quantity",
                "avg_cost",
                "realized_profit",
                "profit_rank",
                "update_time",
            ]
        ]

    def load(self):
        """Load: 将盈亏排名写入 dwd_profit_analysis"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_profit_analysis")

        self.result_df.to_sql(
            "dwd_profit_analysis", conn, if_exists="append", index=False
        )
        conn.commit()
        conn.close()

    def print_report(self):
        """打印盈亏排行榜与 TOP3"""
        df = self.result_df

        print()
        print("=" * 80)
        print("ETF收益贡献排行榜")
        print("=" * 80)

        for _, row in df.iterrows():
            print(
                f"#{row['profit_rank']:>2} "
                f"{row['etf_code']} "
                f"{row['etf_name']:<10} "
                f"收益:{row['realized_profit']:>10.2f}"
            )

        print()

        top3 = df.head(3)

        print("=" * 80)
        print("TOP3收益贡献")
        print("=" * 80)

        for _, row in top3.iterrows():
            print(
                f"{row['etf_name']} "
                f"+{row['realized_profit']:.2f}"
            )

    def run(self):
        super().run()
        self.print_report()


if __name__ == "__main__":
    engine = ProfitEngine()
    engine.run()
