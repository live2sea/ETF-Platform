# -*- coding: utf-8 -*-

"""
仓位再平衡引擎

输入:
    dwd_allocation

输出:
    dwd_rebalance

逻辑:

当前仓位 > 目标仓位 +5%
    减仓

当前仓位 < 目标仓位 -5%
    加仓

否则
    持有
"""

import sqlite3
import pandas as pd
from datetime import datetime


class RebalanceEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

        self.target_allocation = {

            "港股科技": 30,
            "美股科技": 20,
            "美股宽基": 15,
            "红利": 10,
            "日本": 10,
            "印度": 5,
            "欧洲": 5,
            "农业": 3,
            "医疗": 2
        }

        self.category_map = {

            "159740": "港股科技",
            "513580": "港股科技",
            "513980": "港股科技",

            "159632": "美股科技",
            "159696": "美股科技",
            "159659": "美股科技",
            "513110": "美股科技",
            "513300": "美股科技",

            "513400": "美股宽基",

            "510880": "红利",
            "563020": "红利",

            "513000": "日本",
            "513800": "日本",

            "164824": "印度",

            "159561": "欧洲",

            "159865": "农业",

            "512170": "医疗"
        }

    def load_data(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                etf_code,
                etf_name,
                market_value,
                allocation_pct
            FROM dwd_allocation
            """,
            conn
        )

        conn.close()

        return df

    def build_rebalance(self):

        df = self.load_data()

        result = []

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        for _, row in df.iterrows():

            code = row["etf_code"]

            category = self.category_map.get(
                code,
                "其它"
            )

            current_pct = float(
                row["allocation_pct"]
            )

            target_pct = self.target_allocation.get(
                category,
                0
            )

            deviation = round(
                current_pct - target_pct,
                2
            )

            if deviation > 5:

                action = "减仓"

            elif deviation < -5:

                action = "加仓"

            else:

                action = "持有"

            result.append([

                code,
                row["etf_name"],
                category,

                round(
                    row["market_value"],
                    2
                ),

                round(
                    current_pct,
                    2
                ),

                target_pct,

                deviation,

                action,

                now
            ])

        return pd.DataFrame(
            result,
            columns=[
                "etf_code",
                "etf_name",
                "category",

                "current_value",
                "current_pct",

                "target_pct",

                "deviation_pct",

                "action",

                "update_time"
            ]
        )

    def save_result(self, df):

        conn = sqlite3.connect(
            self.db_path
        )

        conn.execute(
            "DELETE FROM dwd_rebalance"
        )

        df.to_sql(
            "dwd_rebalance",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    def print_result(self, df):

        print()
        print("=" * 100)
        print("仓位再平衡建议")
        print("=" * 100)

        for _, row in df.sort_values(
            "deviation_pct",
            ascending=False
        ).iterrows():

            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:10s} "
                f"{row['category']:8s} "
                f"当前:{row['current_pct']:6.2f}% "
                f"目标:{row['target_pct']:5.2f}% "
                f"偏离:{row['deviation_pct']:6.2f}% "
                f"{row['action']}"
            )

    def run(self):

        df = self.build_rebalance()

        self.save_result(df)

        self.print_result(df)


if __name__ == "__main__":

    RebalanceEngine().run()