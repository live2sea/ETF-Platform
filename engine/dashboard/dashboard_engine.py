# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class DashboardEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 加载所有Dashboard所需数据源"""
        conn = sqlite3.connect(self.db_path)
        self.profit_df = pd.read_sql("SELECT * FROM dwd_floating_profit", conn)
        self.category_df = pd.read_sql("SELECT * FROM dwd_category_allocation ORDER BY allocation_pct DESC", conn)
        self.signal_df = pd.read_sql("SELECT * FROM dwd_etf_signal ORDER BY signal_score DESC", conn)
        self.add_df = pd.read_sql("SELECT * FROM dwd_add_position_signal ORDER BY final_score DESC", conn)
        self.risk_df = pd.read_sql("SELECT * FROM dwd_risk_analysis", conn)
        self.rebalance_df = pd.read_sql("SELECT * FROM dwd_rebalance_v2 ORDER BY ABS(deviation_pct) DESC", conn)
        conn.close()

    def transform(self):
        """Transform: 汇总Dashboard指标"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = []

        total_cost = round(self.profit_df["cost_value"].sum(), 2)
        total_market = round(self.profit_df["market_value"].sum(), 2)
        total_profit = round(self.profit_df["floating_profit"].sum(), 2)
        profit_pct = round(total_profit / total_cost * 100, 2)

        rows.extend([
            ["总成本", str(total_cost), now],
            ["总市值", str(total_market), now],
            ["总盈亏", str(total_profit), now],
            ["收益率", f"{profit_pct}%", now],
        ])

        if not self.category_df.empty:
            top1 = self.category_df.iloc[0]
            rows.append(["第一重仓", f"{top1['category_name']} {top1['allocation_pct']:.2f}%", now])

        best_signal = self.signal_df.iloc[0]
        rows.append(["最佳ETF", f"{best_signal['etf_code']} {best_signal['etf_name']} {best_signal['signal_score']}", now])

        add_positive = self.add_df[self.add_df["recommend_amount"] > 0]
        if not add_positive.empty:
            top_add = add_positive.iloc[0]
            rows.append(["推荐加仓", f"{top_add['etf_code']} {top_add['etf_name']} {top_add['recommend_amount']:.0f}", now])

        if not self.risk_df.empty:
            high_risk = self.risk_df[self.risk_df["risk_level"] == "高"]
            rows.append(["高风险项数量", str(len(high_risk)), now])

        if not self.rebalance_df.empty:
            top_dev = self.rebalance_df.iloc[0]
            rows.append(["偏离最大仓位", f"{top_dev['category']} {top_dev['deviation_pct']:.2f}%", now])

        self.result_df = pd.DataFrame(rows, columns=["item_name", "item_value", "update_time"])

    def load(self):
        """Load: 写入 dwd_dashboard"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_dashboard")
        self.result_df.to_sql("dwd_dashboard", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        print()
        print("=" * 100)
        print("ETF驾驶舱")
        print("=" * 100)
        for _, row in self.result_df.iterrows():
            print(f"{row['item_name']:<15}{row['item_value']}")

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    DashboardEngine().run()
