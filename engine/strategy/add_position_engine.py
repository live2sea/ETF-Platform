# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class AddPositionEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 加载信号、仓位、浮动盈亏"""
        conn = sqlite3.connect(self.db_path)
        self.signal_df = pd.read_sql(
            "SELECT etf_code, etf_name, signal_score FROM dwd_etf_signal", conn
        )
        self.allocation_df = pd.read_sql(
            "SELECT etf_code, allocation_pct FROM dwd_allocation", conn
        )
        self.floating_df = pd.read_sql(
            "SELECT etf_code, floating_profit_pct FROM dwd_floating_profit", conn
        )
        conn.close()

    def transform(self):
        """Transform: 综合评分 + 加仓建议"""
        df = (
            self.signal_df.merge(self.allocation_df, on="etf_code", how="left")
            .merge(self.floating_df, on="etf_code", how="left")
        )

        df["floating_score"] = df["floating_profit_pct"].apply(self._calc_floating_score)
        df["allocation_score"] = df["allocation_pct"].apply(self._calc_allocation_score)
        df["final_score"] = (
            df["signal_score"] * 0.5 + df["floating_score"] * 0.2 + df["allocation_score"] * 0.3
        ).round(2)

        df["recommend_amount"] = df["final_score"].apply(self._calc_amount)
        df["recommendation"] = df["final_score"].apply(self._build_advice)
        df["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.result_df = df.sort_values("final_score", ascending=False)

    def _calc_floating_score(self, pct):
        if pd.isna(pct):
            return 50
        if pct <= -15:
            return 100
        if pct <= -10:
            return 80
        if pct <= -5:
            return 60
        return 20

    def _calc_allocation_score(self, pct):
        if pd.isna(pct):
            return 50
        if pct > 20:
            return 0
        if pct > 15:
            return 30
        if pct > 10:
            return 70
        return 100

    def _calc_amount(self, score):
        if score >= 80:
            return 5000
        if score >= 70:
            return 3000
        if score >= 60:
            return 2000
        return 0

    def _build_advice(self, score):
        if score >= 80:
            return "优先加仓"
        if score >= 70:
            return "可以加仓"
        if score >= 60:
            return "小额试仓"
        return "暂不加仓"

    def load(self):
        """Load: 写入 dwd_add_position_signal"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_add_position_signal")
        self.result_df.to_sql("dwd_add_position_signal", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        print()
        print("=" * 100)
        print("今日加仓建议")
        print("=" * 100)
        top_df = self.result_df[self.result_df["recommend_amount"] > 0].head(10)
        for _, row in top_df.iterrows():
            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10}"
                f" 综合分:{row['final_score']:>6}"
                f" 建议金额:{int(row['recommend_amount']):>6}"
                f" 建议:{row['recommendation']}"
            )

    def run(self):
        super().run()
        self.print_result()
        print()
        print(f"生成加仓建议 {len(self.result_df)} 条")


if __name__ == "__main__":
    AddPositionEngine().run()
