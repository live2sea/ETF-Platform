# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class ETFScoreEngineV2(BaseEngine):
    """ETF评分系统 V2"""

    def __init__(self):
        super().__init__()
        self._category_map = {
            "159740": "港股科技", "513580": "港股科技", "513980": "港股科技",
            "159632": "美股科技", "159696": "美股科技", "513300": "美股科技",
            "513110": "美股科技", "159659": "美股科技",
            "513400": "美股宽基",
            "510880": "红利", "563020": "红利",
            "164824": "印度",
            "513000": "日本", "513800": "日本",
            "159865": "农业",
            "512170": "医疗",
            "159529": "消费",
            "159561": "欧洲",
        }

    def extract(self):
        """Extract: 加载仓位、浮动盈亏、已实现收益"""
        conn = sqlite3.connect(self.db_path)
        self.allocation_df = pd.read_sql(
            "SELECT etf_code, etf_name, allocation_pct FROM dwd_allocation", conn
        )
        self.floating_df = pd.read_sql(
            "SELECT etf_code, floating_profit, floating_profit_pct FROM dwd_floating_profit", conn
        )
        self.profit_df = pd.read_sql(
            "SELECT etf_code, realized_profit FROM dwd_profit_analysis", conn
        )
        conn.close()

    def transform(self):
        """Transform: 综合评分计算"""
        df = (
            self.allocation_df.merge(self.floating_df, on="etf_code", how="left")
            .merge(self.profit_df, on="etf_code", how="left")
        )
        df.fillna(0, inplace=True)

        result = []
        for _, row in df.iterrows():
            total_score = sum([
                self._calc_allocation_score(row["allocation_pct"]),
                self._calc_floating_score(row["floating_profit_pct"]),
                self._calc_realized_score(row["realized_profit"]),
            ])
            result.append({
                "etf_code": row["etf_code"],
                "etf_name": row["etf_name"],
                "category_name": self._category_map.get(row["etf_code"], "其它"),
                "allocation_pct": round(row["allocation_pct"], 2),
                "floating_profit": round(row["floating_profit"], 2),
                "floating_profit_pct": round(row["floating_profit_pct"], 2),
                "realized_profit": round(row["realized_profit"], 2),
                "total_score": total_score,
                "score_level": self._get_level(total_score),
                "suggestion": self._get_suggestion(total_score),
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

        self.result_df = pd.DataFrame(result).sort_values("total_score", ascending=False)

    def _calc_allocation_score(self, pct):
        if pct <= 5: return 20
        if pct <= 10: return 15
        if pct <= 20: return 10
        if pct <= 30: return 5
        return 0

    def _calc_floating_score(self, pct):
        if pct >= 15: return 15
        if pct >= 5: return 12
        if pct >= 0: return 10
        if pct >= -10: return 6
        if pct >= -20: return 3
        return 0

    def _calc_realized_score(self, profit):
        if profit >= 5000: return 15
        if profit >= 2000: return 12
        if profit > 0: return 8
        return 3

    def _get_level(self, score):
        if score >= 80: return "A"
        if score >= 65: return "B"
        if score >= 50: return "C"
        return "D"

    def _get_suggestion(self, score):
        if score >= 80: return "优先加仓"
        if score >= 65: return "继续持有"
        if score >= 50: return "观察"
        return "减仓观察"

    def load(self):
        """Load: 写入 dwd_etf_score_v2"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_etf_score_v2")
        self.result_df.to_sql("dwd_etf_score_v2", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        print()
        print("=" * 100)
        print("ETF评分V2排行榜")
        print("=" * 100)
        for _, row in self.result_df.iterrows():
            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10}"
                f" 总分:{row['total_score']:>3}"
                f" 等级:{row['score_level']}"
                f" 建议:{row['suggestion']}"
            )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    ETFScoreEngineV2().run()
