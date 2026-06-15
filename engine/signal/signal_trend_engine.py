# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class SignalTrendEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 加载信号历史"""
        conn = sqlite3.connect(self.db_path)
        self.history_df = pd.read_sql(
            """
            SELECT trade_date, etf_code, etf_name, signal_score
            FROM dwd_signal_history
            ORDER BY trade_date
            """,
            conn,
        )
        conn.close()

    def transform(self):
        """Transform: 计算信号变化趋势"""
        df = self.history_df
        if df.empty:
            self.result_df = pd.DataFrame()
            return

        dates = sorted(df["trade_date"].unique())
        if len(dates) < 2:
            print("历史数据不足2天")
            self.result_df = pd.DataFrame()
            return

        today, yesterday = dates[-1], dates[-2]
        today_df = df[df["trade_date"] == today]
        yesterday_df = df[df["trade_date"] == yesterday]

        result = today_df.merge(
            yesterday_df[["etf_code", "signal_score"]],
            on="etf_code",
            how="left",
            suffixes=("_today", "_yesterday"),
        )
        result.rename(
            columns={"signal_score_today": "today_score", "signal_score_yesterday": "yesterday_score"},
            inplace=True,
        )
        result["yesterday_score"] = result["yesterday_score"].fillna(result["today_score"])
        result["change_score"] = result["today_score"] - result["yesterday_score"]

        def _get_trend(x):
            if x >= 5:
                return "显著增强"
            elif x > 0:
                return "增强"
            elif x <= -5:
                return "显著走弱"
            elif x < 0:
                return "走弱"
            return "持平"

        result["trend"] = result["change_score"].apply(_get_trend)
        result["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.result_df = result[
            ["etf_code", "etf_name", "today_score", "yesterday_score", "change_score", "trend", "update_time"]
        ]

    def load(self):
        """Load: 写入 dwd_signal_trend"""
        if self.result_df.empty:
            return
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_signal_trend")
        self.result_df.to_sql("dwd_signal_trend", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()
        print(f"[OK] 写入{len(self.result_df)}条趋势记录")

    def print_result(self):
        if self.result_df.empty:
            return
        print()
        print("=" * 80)
        print("ETF评分趋势分析")
        print("=" * 80)
        print(self.result_df.sort_values("change_score", ascending=False).head(10))

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    SignalTrendEngine().run()
