# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class ReviewEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 加载所有复盘所需数据"""
        conn = sqlite3.connect(self.db_path)
        self.dashboard_df = pd.read_sql(
            "SELECT item_name, item_value FROM dwd_dashboard", conn
        )
        self.signal_df = pd.read_sql(
            "SELECT etf_code, etf_name, signal_score FROM dwd_etf_signal", conn
        )
        self.risk_df = pd.read_sql(
            "SELECT risk_level FROM dwd_risk_analysis", conn
        )
        self.add_df = pd.read_sql(
            "SELECT etf_code, etf_name, final_score, recommend_amount FROM dwd_add_position_signal ORDER BY final_score DESC",
            conn,
        )
        conn.close()

    def transform(self):
        """Transform: 构建每日复盘报告"""
        dashboard_map = dict(zip(self.dashboard_df["item_name"], self.dashboard_df["item_value"]))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = []

        rows.append(["总资产", dashboard_map.get("总市值", "-"), now])
        rows.append(["总盈亏", dashboard_map.get("总盈亏", "-"), now])
        rows.append(["收益率", dashboard_map.get("收益率", "-"), now])

        if not self.signal_df.empty:
            best = self.signal_df.sort_values("signal_score", ascending=False).iloc[0]
            worst = self.signal_df.sort_values("signal_score", ascending=True).iloc[0]
            rows.append(["最佳ETF", f"{best['etf_code']} {best['etf_name']}", now])
            rows.append(["最差ETF", f"{worst['etf_code']} {worst['etf_name']}", now])

        if not self.add_df.empty:
            top_add = self.add_df.iloc[0]
            rows.append(["推荐加仓", f"{top_add['etf_code']} {top_add['etf_name']}", now])

        risk_count = len(self.risk_df[self.risk_df["risk_level"].isin(["高", "HIGH"])])
        rows.append(["高风险项数量", str(risk_count), now])

        best_name = self.signal_df.iloc[0]["etf_name"] if not self.signal_df.empty else ""
        profit_pct = dashboard_map.get("收益率", "-")
        summary = f"当前组合收益率{profit_pct}，最佳ETF为{best_name}，当前高风险项{risk_count}个，建议优先关注综合评分靠前ETF。"
        rows.append(["AI总结", summary, now])

        self.result_df = pd.DataFrame(rows, columns=["review_item", "review_value", "update_time"])

    def load(self):
        """Load: 写入 dwd_daily_review"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_daily_review")
        self.result_df.to_sql("dwd_daily_review", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        print()
        print("=" * 80)
        print("ETF每日复盘")
        print("=" * 80)
        for _, row in self.result_df.iterrows():
            print(f"{row['review_item']:<10} : {row['review_value']}")

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    ReviewEngine().run()
