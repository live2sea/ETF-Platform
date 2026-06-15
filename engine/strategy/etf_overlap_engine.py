# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class ETFOverlapEngine(BaseEngine):

    def __init__(self):
        super().__init__()
        self.etf_group = {
            "纳斯达克100": ["159632", "159696", "159659", "513110", "513300"],
            "港股科技": ["159740", "513580", "513980"],
            "日本": ["513000", "513800"],
            "红利": ["510880", "563020"],
        }

    def extract(self):
        """Extract: 加载仓位分配"""
        conn = sqlite3.connect(self.db_path)
        self.allocation_df = pd.read_sql(
            "SELECT etf_code, etf_name, market_value, allocation_pct FROM dwd_allocation",
            conn,
        )
        conn.close()

    def transform(self):
        """Transform: 检测重叠持仓"""
        df = self.allocation_df
        total_value = df["market_value"].sum()
        result = []

        for group_name, codes in self.etf_group.items():
            group_df = df[df["etf_code"].isin(codes)]
            if group_df.empty:
                continue

            etf_count = len(group_df)
            group_value = group_df["market_value"].sum()
            allocation_pct = round(group_value / total_value * 100, 2)
            risk_level = self._calc_risk_level(etf_count, allocation_pct)

            if risk_level == "危险":
                suggestion = "建议合并持仓"
            elif risk_level == "注意":
                suggestion = "控制新增仓位"
            else:
                suggestion = "保持"

            result.append({
                "group_name": group_name,
                "etf_count": etf_count,
                "total_value": round(group_value, 2),
                "allocation_pct": allocation_pct,
                "risk_level": risk_level,
                "suggestion": suggestion,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

        self.result_df = pd.DataFrame(result)

    def _calc_risk_level(self, etf_count, allocation_pct):
        if etf_count >= 4:
            return "危险"
        if etf_count >= 3 and allocation_pct > 10:
            return "危险"
        if etf_count >= 2:
            return "注意"
        return "正常"

    def load(self):
        """Load: 写入 dwd_etf_overlap"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS dwd_etf_overlap (group_name TEXT, etf_count INTEGER, total_value REAL, allocation_pct REAL, risk_level TEXT, suggestion TEXT, update_time TEXT)")
        conn.execute("DELETE FROM dwd_etf_overlap")
        self.result_df.to_sql("dwd_etf_overlap", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        print()
        print("=" * 100)
        print("ETF重叠分析")
        print("=" * 100)
        for _, row in self.result_df.iterrows():
            print(
                f"{row['group_name']:10}"
                f" ETF数:{row['etf_count']:2}"
                f" 占比:{row['allocation_pct']:6.2f}%"
                f" 风险:{row['risk_level']}"
                f" 建议:{row['suggestion']}"
            )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    ETFOverlapEngine().run()
