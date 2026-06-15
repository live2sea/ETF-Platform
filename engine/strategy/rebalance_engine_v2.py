# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class RebalanceEngineV2(BaseEngine):

    def __init__(self):
        super().__init__()
        self.target_allocation = {
            "港股科技": 30, "美股科技": 20, "美股宽基": 15,
            "日本": 10, "红利": 10, "印度": 5, "欧洲": 5,
            "医疗": 2, "农业": 3,
        }

    def extract(self):
        """Extract: 加载分类仓位"""
        conn = sqlite3.connect(self.db_path)
        self.category_df = pd.read_sql("SELECT * FROM dwd_category_allocation", conn)
        conn.close()

    def transform(self):
        """Transform: 按分类计算再平衡建议"""
        df = self.category_df
        if df.empty:
            self.result_df = pd.DataFrame()
            return

        total_value = df["market_value"].sum()
        rows = []

        for _, row in df.iterrows():
            category = row["category_name"]
            current_pct = float(row["allocation_pct"])
            target_pct = self.target_allocation.get(category, current_pct)
            deviation_pct = round(current_pct - target_pct, 2)
            target_value = total_value * target_pct / 100
            suggest_amount = round(target_value - float(row["market_value"]), 2)

            if deviation_pct >= 5:
                action = "减仓"
            elif deviation_pct <= -5:
                action = "加仓"
            else:
                action = "持有"

            rows.append({
                "category": category,
                "current_value": round(float(row["market_value"]), 2),
                "current_pct": round(current_pct, 2),
                "target_pct": round(target_pct, 2),
                "deviation_pct": deviation_pct,
                "action": action,
                "suggest_amount": suggest_amount,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

        self.result_df = pd.DataFrame(rows).sort_values("deviation_pct", ascending=False)

    def load(self):
        """Load: 写入 dwd_rebalance_v2"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_rebalance_v2")
        self.result_df.to_sql("dwd_rebalance_v2", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        print()
        print("=" * 100)
        print("主题仓位再平衡建议")
        print("=" * 100)
        for _, row in self.result_df.iterrows():
            print(
                f"{row['category']:10}"
                f" 当前:{row['current_pct']:6.2f}%"
                f" 目标:{row['target_pct']:6.2f}%"
                f" 偏离:{row['deviation_pct']:6.2f}%"
                f" 建议:{row['action']:4}"
                f" 金额:{row['suggest_amount']:10.0f}"
            )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    RebalanceEngineV2().run()
