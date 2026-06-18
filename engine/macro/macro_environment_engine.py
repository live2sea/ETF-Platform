# -*- coding: utf-8 -*-

import os
import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class MacroEnvironmentEngine(BaseEngine):
    """宏观环境引擎: 加权总分 + 趋势加速度 + 阶段判定 + 仓位上限"""

    PHASES = ["扩张", "复苏", "观望", "防御"]

    def __init__(self):
        super().__init__()
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "config", "macro_weights.json"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def extract(self):
        conn = sqlite3.connect(self.db_path)
        self.indicator_df = pd.read_sql(
            "SELECT indicator_date, indicator_name, indicator_value, score FROM dwd_macro_indicator ORDER BY indicator_date",
            conn
        )
        conn.close()
        if self.indicator_df.empty:
            print("[WARN] dwd_macro_indicator is empty")

    def _determine_phase(self, macro_score):
        thresholds = self.config["phase_thresholds"]
        if macro_score >= thresholds["扩张"]:
            return "扩张"
        if macro_score >= thresholds["复苏"]:
            return "复苏"
        if macro_score >= thresholds["观望"]:
            return "观望"
        return "防御"

    def _calc_trend_score(self, latest_date):
        trend_cfg = self.config["trend"]
        lookback = trend_cfg["lookback_months"]
        date_series = sorted(self.indicator_df["indicator_date"].unique())
        if len(date_series) < 2:
            return 0.0
        idx = date_series.index(latest_date) if latest_date in date_series else -1
        if idx <= 0:
            return 0.0
        prev_date = date_series[max(0, idx - 1)]
        indicators_cfg = self.config["indicators"]
        total_weight = sum(v["weight"] for v in indicators_cfg.values()) or 1.0
        trend_sum = 0.0
        now_data = self.indicator_df[self.indicator_df["indicator_date"] == latest_date]
        prev_data = self.indicator_df[self.indicator_df["indicator_date"] == prev_date]
        for name, cfg in indicators_cfg.items():
            w = cfg["weight"] / total_weight
            n_row = now_data[now_data["indicator_name"] == name]
            p_row = prev_data[prev_data["indicator_name"] == name]
            if n_row.empty or p_row.empty:
                continue
            nv = float(n_row.iloc[0]["indicator_value"])
            pv = float(p_row.iloc[0]["indicator_value"])
            diff = nv - pv
            if abs(diff) < 1e-9:
                continue
            trend_sum += (1.0 if diff > 0 else -1.0) * w
        return round(trend_sum, 4)

    def _determine_acceleration(self, trend_score):
        tc = self.config["trend"]
        if trend_score > tc["positive_threshold"]:
            return "正向"
        if trend_score < tc["negative_threshold"]:
            return "负向"
        return "中性"

    def _effective_phase(self, static_phase, acceleration):
        matrix = self.config["phase_correction_matrix"]
        if static_phase in matrix and acceleration in matrix[static_phase]:
            return matrix[static_phase][acceleration]
        return static_phase

    def transform(self):
        if self.indicator_df.empty:
            self.result_df = pd.DataFrame()
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latest_date = self.indicator_df["indicator_date"].max()
        latest = self.indicator_df[self.indicator_df["indicator_date"] == latest_date]
        indicators_cfg = self.config["indicators"]
        total_weight = sum(v["weight"] for v in indicators_cfg.values()) or 1.0
        macro_score = 0.0
        for _, row in latest.iterrows():
            name = row["indicator_name"]
            score = float(row["score"])
            w = indicators_cfg.get(name, {}).get("weight", 0)
            macro_score += score * w / total_weight
        macro_score = round(macro_score, 1)
        static_phase = self._determine_phase(macro_score)
        trend_score = self._calc_trend_score(latest_date)
        acceleration = self._determine_acceleration(trend_score)
        effective_phase = self._effective_phase(static_phase, acceleration)
        position_cap = self.config["phase_position_caps"].get(effective_phase, 60)
        self.result_df = pd.DataFrame([{
            "eval_date": latest_date,
            "macro_score": macro_score,
            "macro_phase": static_phase,
            "trend_score": trend_score,
            "acceleration": acceleration,
            "effective_phase": effective_phase,
            "position_cap": position_cap,
            "update_time": now
        }])

    def load(self):
        if self.result_df.empty:
            return
        conn = sqlite3.connect(self.db_path)
        for _, row in self.result_df.iterrows():
            conn.execute(
                "INSERT OR REPLACE INTO dwd_macro_environment (eval_date, macro_score, macro_phase, trend_score, acceleration, effective_phase, position_cap, update_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (row["eval_date"], row["macro_score"], row["macro_phase"],
                 row["trend_score"], row["acceleration"], row["effective_phase"],
                 int(row["position_cap"]), row["update_time"])
            )
        conn.commit()
        conn.close()
        print(f"Saved to dwd_macro_environment")

    def print_result(self):
        print()
        print("=" * 100)
        print("宏观环境评估")
        print("=" * 100)
        if self.result_df.empty:
            print("  (no data)")
            return
        row = self.result_df.iloc[0]
        print(f"  Score={row['macro_score']}  Phase={row['macro_phase']}  Trend={row['trend_score']}  Accel={row['acceleration']}")
        print(f"  Effective={row['effective_phase']}  Cap={row['position_cap']}%")

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    MacroEnvironmentEngine().run()
