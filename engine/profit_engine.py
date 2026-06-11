#!/usr/bin/env python3
#解释：该脚本定义了一个ProfitEngine类，用于计算ETF的盈亏情况。它从SQLite数据库中加载当前持仓数据，计算每只ETF的盈亏金额和排名，并将结果保存到数据库中的盈亏分析表中。最后，在主程序中创建一个ProfitEngine实例，执行计算并打印盈亏排行榜和TOP3盈亏贡献。   

import sqlite3
import pandas as pd
from datetime import datetime


class ProfitEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    def load_position(self):

        conn = sqlite3.connect(
            self.db_path
        )

        df = pd.read_sql(
            """
            SELECT *
            FROM dwd_position
            """,
            conn
        )

        conn.close()

        return df

    def build_profit_ranking(self):

        df = self.load_position()

        df = df.sort_values(
            by="realized_profit",
            ascending=False
        )

        df["profit_rank"] = range(
            1,
            len(df) + 1
        )

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        df["update_time"] = now

        return df[
            [
                "etf_code",
                "etf_name",
                "quantity",
                "avg_cost",
                "realized_profit",
                "profit_rank",
                "update_time"
            ]
        ]

    def save_result(self, df):

        conn = sqlite3.connect(
            self.db_path
        )

        conn.execute(
            "DELETE FROM dwd_profit_analysis"
        )

        df.to_sql(
            "dwd_profit_analysis",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    def print_report(self, df):

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

        df = self.build_profit_ranking()

        self.save_result(df)

        self.print_report(df)


if __name__ == "__main__":

    engine = ProfitEngine()

    engine.run()