# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class RiskEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 加载仓位与分类数据"""
        conn = sqlite3.connect(self.db_path)
        self.allocation_df = pd.read_sql("SELECT * FROM dwd_allocation", conn)
        self.category_df = pd.read_sql("SELECT * FROM dwd_category_allocation", conn)
        conn.close()

    def transform(self):
        """Transform: 构建风险分析"""
        risk_rows = []
        score = 100

        for _, row in self.allocation_df.iterrows():
            pct = float(row["allocation_pct"])
            if pct >= 20:
                level = "高"; score -= 10
            elif pct >= 15:
                level = "中"
            else:
                level = "低"
            risk_rows.append(["ETF", row["etf_name"], round(pct, 2), level, "单只ETF建议不超过15%"])

        for _, row in self.category_df.iterrows():
            pct = float(row["allocation_pct"])
            if pct >= 40:
                level = "高"; score -= 15
            elif pct >= 30:
                level = "中"
            else:
                level = "低"
            risk_rows.append(["主题", row["category_name"], round(pct, 2), level, "单主题建议不超过30%"])

        self.result_df = pd.DataFrame(
            risk_rows, columns=["risk_type", "risk_name", "risk_value", "risk_level", "suggestion"]
        )
        self.result_df["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.risk_score = max(score, 0)

    def load(self):
        """Load: 写入 dwd_risk_analysis"""
        conn = sqlite3.connect(self.db_path)
        self.result_df.to_sql("dwd_risk_analysis", conn, if_exists="replace", index=False)
        conn.close()

    def show_result(self):
        df = self.result_df
        score = self.risk_score

        print()
        print("=" * 100)
        print("组合风险分析")
        print("=" * 100)
        print(f"风险评分：{score}")

        if score >= 80: level = "A"
        elif score >= 60: level = "B"
        elif score >= 40: level = "C"
        else: level = "D"
        print(f"风险等级：{level}")
        print()

        high_risk = df[df["risk_level"] == "高"]
        if not high_risk.empty:
            print("高风险项目")
            print("-" * 100)
            for _, row in high_risk.iterrows():
                print(f"{row['risk_type']} {row['risk_name']} {row['risk_value']:.2f}%")

    def run(self):
        super().run()
        self.show_result()


if __name__ == "__main__":
    RiskEngine().run()
