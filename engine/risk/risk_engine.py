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
        conn = sqlite3.connect(self.db_path)
        self.allocation_df = pd.read_sql("SELECT * FROM dwd_allocation", conn)
        self.category_df = pd.read_sql("SELECT * FROM dwd_category_allocation", conn)
        try:
            self.macro_env = pd.read_sql(
                "SELECT effective_phase, position_cap FROM dwd_macro_environment ORDER BY eval_date DESC LIMIT 1", conn
            )
        except Exception:
            self.macro_env = pd.DataFrame()
        conn.close()

    def transform(self):
        risk_rows = []
        score = 100

        for _, row in self.allocation_df.iterrows():
            pct = float(row["allocation_pct"])
            if pct >= 20:
                level = "高"
                score -= 10
            elif pct >= 15:
                level = "中"
            else:
                level = "低"
            risk_rows.append(["ETF", row["etf_name"], round(pct, 2), level,
                              "单只ETF建议不超过15%"])

        for _, row in self.category_df.iterrows():
            pct = float(row["allocation_pct"])
            if pct >= 40:
                level = "高"
                score -= 15
            elif pct >= 30:
                level = "中"
            else:
                level = "低"
            risk_rows.append(["主题", row["category_name"], round(pct, 2), level,
                              "单主题建议不超过30%"])

        # --- macro position cap analysis ---
        if not self.macro_env.empty:
            cap = int(self.macro_env.iloc[0]["position_cap"])
            phase = self.macro_env.iloc[0]["effective_phase"]
            actual = round(float(category_df["allocation_pct"].sum()), 1) if "category_df" in dir() and self.category_df is not None and not self.category_df.empty else 0
            # recalc actual total from allocation_df
            actual_total = round(float(self.allocation_df["allocation_pct"].sum()), 1)
            cap_gap = round(actual_total - cap, 1)
            warning = ""
            if cap_gap > 0:
                warning = f"超限{cap_gap:.1f}% | 建议减仓至≤{cap}%"
                score -= 15
            risk_rows.append(["宏观仓位", f"effective_phase={phase}",
                              cap, "高" if gap > 0 else "低",
                              f"仓位上限={cap}%, 实际={actual_total:.1f}%{', ' + warning if warning else ''}"])

        self.macro_position_cap = int(self.macro_env.iloc[0]["position_cap"]) if not self.macro_env.empty else 0
        self.result_df = pd.DataFrame(
            risk_rows, columns=["risk_type", "risk_name", "risk_value", "risk_level", "suggestion"]
        )
        self.result_df["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.risk_score = max(score, 0)

    def load(self):
        conn = sqlite3.connect(self.db_path)
        self.result_df.to_sql("dwd_risk_analysis", conn, if_exists="replace", index=False)
        conn.close()

    def show_result(self):
        df = self.result_df
        score = self.risk_score
        print()
        print("=" * 100)
        print("组合风险分析 (含宏观仓位上限)")
        print("=" * 100)
        print(f"风险评分: {score}")
        if score >= 80: level = "A"
        elif score >= 60: level = "B"
        elif score >= 40: level = "C"
        else: level = "D"
        print(f"风险等级: {level}")
        if self.macro_position_cap > 0:
            print(f"宏观仓位上限: {self.macro_position_cap}%")
        print()
        high_risk = df[df["risk_level"] == "高"]
        if not high_risk.empty:
            print("高风险项目:")
            print("-" * 100)
            for _, row in high_risk.iterrows():
                print(f"  {row['risk_type']} {row['risk_name']} {row['risk_value']:.2f}%")

    def run(self):
        super().run()
        self.show_result()


if __name__ == "__main__":
    RiskEngine().run()
