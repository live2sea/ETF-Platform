# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class ETFSignalEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 从三个因子表加载评分数据"""
        conn = sqlite3.connect(self.db_path)

        ma_df = pd.read_sql(
            "SELECT etf_code, etf_name, trend_score AS ma_score FROM dwd_ma_factor",
            conn,
        )
        rsi_df = pd.read_sql(
            "SELECT etf_code, score AS rsi_score FROM dwd_rsi_factor",
            conn,
        )
        drawdown_df = pd.read_sql(
            "SELECT etf_code, score AS drawdown_score FROM dwd_drawdown_factor",
            conn,
        )
        conn.close()

        self.factor_df = (
            ma_df.merge(rsi_df, on="etf_code", how="left")
            .merge(drawdown_df, on="etf_code", how="left")
        )
        self.factor_df.fillna(0, inplace=True)

    def transform(self):
        """Transform: 加权计算综合信号"""
        df = self.factor_df

        df["signal_score"] = df.apply(self._calculate_score, axis=1)
        levels = df["signal_score"].apply(self._evaluate)
        df["level"] = levels.apply(lambda x: x[0])
        df["suggestion"] = levels.apply(lambda x: x[1])
        df["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.result_df = df

    def _calculate_score(self, row):
        return round(
            row["ma_score"] * 0.4 + row["rsi_score"] * 0.3 + row["drawdown_score"] * 0.3, 2
        )

    def _evaluate(self, score):
        if score >= 85:
            return "S", "重点加仓"
        elif score >= 70:
            return "A", "优先加仓"
        elif score >= 55:
            return "B", "可以关注"
        elif score >= 40:
            return "C", "继续观察"
        else:
            return "D", "暂停加仓"

    def load(self):
        """Load: 写入信号表 + 历史记录"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_etf_signal")
        self.result_df.to_sql("dwd_etf_signal", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

        # 历史记录
        today_str = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_signal_history WHERE trade_date = ?", (today_str,))
        history_df = self.result_df.copy()
        history_df["trade_date"] = today_str
        history_df.to_sql("dwd_signal_history", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()
        print(f"历史信号保存：{len(self.result_df)}条")

    def print_result(self):
        df = self.result_df.sort_values("signal_score", ascending=False)
        print()
        print("=" * 100)
        print("ETF综合信号排行榜")
        print("=" * 100)
        for _, row in df.iterrows():
            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10} "
                f"总分:{row['signal_score']:>6} "
                f"等级:{row['level']} "
                f"建议:{row['suggestion']}"
            )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    ETFSignalEngine().run()
