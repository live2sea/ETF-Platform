# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class DrawdownEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 读取K线数据"""
        conn = sqlite3.connect(self.db_path)
        self.kline_df = pd.read_sql(
            "SELECT * FROM ods_market_kline ORDER BY etf_code, trade_date",
            conn,
        )
        conn.close()

    def transform(self):
        """Transform: 计算每只ETF的52周回撤"""
        result = []
        for code, group in self.kline_df.groupby("etf_code"):
            if len(group) < 30:
                continue
            result.append(self._build_single(group))
        self.result_df = pd.DataFrame(result)

    def _build_single(self, df):
        df = df.sort_values("trade_date")
        etf_code = df.iloc[-1]["etf_code"]
        etf_name = df.iloc[-1]["etf_name"]
        close_series = df["close_price"].astype(float)
        current_price = float(close_series.iloc[-1])

        lookback_df = df.tail(252)
        high_52w = float(lookback_df["close_price"].max())
        low_52w = float(lookback_df["close_price"].min())
        drawdown_pct = (current_price - high_52w) / high_52w * 100

        score, level, signal = self._evaluate(drawdown_pct)
        return {
            "etf_code": etf_code,
            "etf_name": etf_name,
            "current_price": round(current_price, 3),
            "high_52w": round(high_52w, 3),
            "low_52w": round(low_52w, 3),
            "drawdown_pct": round(drawdown_pct, 2),
            "score": score,
            "level": level,
            "signal": signal,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _evaluate(self, drawdown):
        if drawdown <= -40:
            return 100, "S", "强烈加仓"
        elif drawdown <= -30:
            return 90, "A", "加仓"
        elif drawdown <= -20:
            return 70, "B", "关注"
        elif drawdown <= -10:
            return 50, "C", "观察"
        elif drawdown <= -5:
            return 30, "C", "谨慎"
        else:
            return 10, "D", "追高风险"

    def load(self):
        """Load: 写入 dwd_drawdown_factor"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_drawdown_factor")
        self.result_df.to_sql("dwd_drawdown_factor", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        df = self.result_df.sort_values("drawdown_pct")
        print()
        print("=" * 100)
        print("52周回撤排行榜")
        print("=" * 100)
        for _, row in df.iterrows():
            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10} "
                f"回撤:{row['drawdown_pct']:>7}% "
                f"等级:{row['level']} "
                f"信号:{row['signal']}"
            )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    DrawdownEngine().run()
