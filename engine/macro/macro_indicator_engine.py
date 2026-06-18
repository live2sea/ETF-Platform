# -*- coding: utf-8 -*-

import os
import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class MacroIndicatorEngine(BaseEngine):
    """宏观指标引擎: 读取 ODS 表, 分段线性评分, 增量写入 dwd_macro_indicator"""

    def __init__(self):
        super().__init__()
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "config", "macro_weights.json"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.score_ranges = self.config["score_ranges"]
        self.trend_cfg = self.config["trend"]

    def extract(self):
        conn = sqlite3.connect(self.db_path)
        self.ods_df = pd.read_sql(
            "SELECT indicator_date, indicator_name, indicator_value FROM ods_macro_indicator ORDER BY indicator_date",
            conn
        )
        conn.close()
        if self.ods_df.empty:
            print("[WARN] ods_macro_indicator is empty")

    def _linear_score(self, raw, anchors):
        """分段线性插值评分"""
        if raw is None:
            return 50
        for i in range(len(anchors) - 1):
            x1, y1 = anchors[i]
            x2, y2 = anchors[i + 1]
            if x1 <= raw <= x2:
                if x2 == x1:
                    return int(round((y1 + y2) / 2))
                return int(round(y1 + (y2 - y1) * (raw - x1) / (x2 - x1)))
        if raw < anchors[0][0]:
            return anchors[0][1]
        return anchors[-1][1]

    def _calc_score(self, name, value):
        cfg = self.score_ranges.get(name)
        if cfg is None:
            return 50
        return self._linear_score(value, cfg["anchors"])

    def _calc_trend(self, name, current_val, indicator_date):
        """当前值 vs 上一条记录 的方向"""
        if self.ods_df is None or self.ods_df.empty:
            return "持平"
        hist = self.ods_df[
            (self.ods_df["indicator_name"] == name) &
            (self.ods_df["indicator_date"] < indicator_date)
        ].sort_values("indicator_date", ascending=False)
        if hist.empty:
            return "持平"
        old_val = float(hist.iloc[0]["indicator_value"])
        diff = current_val - old_val
        if abs(diff) < 0.001 * max(abs(current_val), 1):
            return "持平"
        if diff > 0:
            return "上升"
        return "下降"

    def transform(self):
        if self.ods_df.empty:
            self.result_df = pd.DataFrame()
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latest_date = self.ods_df["indicator_date"].max()
        latest = self.ods_df[self.ods_df["indicator_date"] == latest_date]
        rows = []
        for _, row in latest.iterrows():
            name = row["indicator_name"]
            val = float(row["indicator_value"])
            score = self._calc_score(name, val)
            trend = self._calc_trend(name, val, latest_date)
            comment = f"raw={val:.2f}, score={score}"
            rows.append([latest_date, name, val, score, trend, comment, now])
        self.result_df = pd.DataFrame(rows, columns=[
            "indicator_date", "indicator_name", "indicator_value",
            "score", "trend", "comment", "update_time"
        ])

    def load(self):
        if self.result_df.empty:
            return
        conn = sqlite3.connect(self.db_path)
        for _, row in self.result_df.iterrows():
            conn.execute(
                "INSERT OR REPLACE INTO dwd_macro_indicator (indicator_date, indicator_name, indicator_value, score, trend, comment, update_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (row["indicator_date"], row["indicator_name"], row["indicator_value"],
                 int(row["score"]), row["trend"], row["comment"], row["update_time"])
            )
        conn.commit()
        conn.close()
        print(f"Saved {len(self.result_df)} rows to dwd_macro_indicator")

    def print_result(self):
        print()
        print("=" * 100)
        print("宏观指标评分汇总")
        print("=" * 100)
        if self.result_df.empty:
            print("  (no data)")
            return
        for _, row in self.result_df.iterrows():
            print(f"  {row['indicator_name']:<16} raw={row['indicator_value']:>8.2f}  score={int(row['score']):>3}  trend={row['trend']}")

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    MacroIndicatorEngine().run()
