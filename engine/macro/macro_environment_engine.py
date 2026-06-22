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
        indicators_cfg = self.config["indicators"]
        score_ranges = self.config["score_ranges"]
        all_weights = {name: cfg["weight"] for name, cfg in indicators_cfg.items()}
        total_weight = sum(all_weights.values()) or 1.0

        # Parse latest_date to datetime
        try:
            from datetime import datetime, timedelta
            eval_dt = datetime.strptime(latest_date, "%Y-%m-%d")
        except ValueError:
            return 0.0

        # Compute target date: eval_date - lookback_months
        target_year = eval_dt.year
        target_month = eval_dt.month - lookback
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        target_day = min(eval_dt.day, 28)
        target_dt = datetime(target_year, target_month, target_day)

        # Window: target_dt +/- 15 days
        window_start = (target_dt - timedelta(days=15)).strftime("%Y-%m-%d")
        window_end   = (target_dt + timedelta(days=15)).strftime("%Y-%m-%d")

        # Get current scores (indicator_date <= eval_date, latest per indicator)
        current = self.indicator_df[self.indicator_df["indicator_date"] <= latest_date]
        current = current.sort_values("indicator_date").groupby("indicator_name").tail(1)

        # Get comparison scores (indicator_date in window, latest per indicator)
        compare = self.indicator_df[
            (self.indicator_df["indicator_date"] >= window_start) &
            (self.indicator_df["indicator_date"] <= window_end)
        ]
        compare = compare.sort_values("indicator_date").groupby("indicator_name").tail(1)

        used_weight = 0.0
        trend_sum = 0.0

        for name, cfg in indicators_cfg.items():
            w = cfg["weight"]
            cur_row = current[current["indicator_name"] == name]
            cmp_row = compare[compare["indicator_name"] == name]
            if cur_row.empty or cmp_row.empty:
                continue  # skip, weight renormalized
            cur_score = float(cur_row.iloc[0]["score"])
            cmp_score = float(cmp_row.iloc[0]["score"])
            delta = cur_score - cmp_score
            if abs(delta) < 1e-6:
                continue
            # Determine sign: reverse indicators invert
            sr_type = score_ranges.get(name, {}).get("type", "")
            if sr_type == "\u53cd\u5411":
                direction = -1.0 if delta > 0 else 1.0
            else:
                direction = 1.0 if delta > 0 else -1.0
            trend_sum += direction * w
            used_weight += w

        # Normalize by used weight (skip unavailable indicators)
        if used_weight > 0:
            trend_sum = trend_sum * (total_weight / used_weight)

        return round(trend_sum / total_weight, 4)

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
