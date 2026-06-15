# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class RSIFactorEngine(BaseEngine):

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
        """Transform: 计算每只ETF的RSI因子"""
        result = []
        for code, group in self.kline_df.groupby("etf_code"):
            if len(group) < 30:
                continue
            row = self._build_single(group)
            result.append(row)
        self.result_df = pd.DataFrame(result)

    def _calc_rsi(self, close_series, period=14):
        delta = close_series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _build_single(self, df):
        df = df.sort_values("trade_date")
        etf_code = df.iloc[-1]["etf_code"]
        etf_name = df.iloc[-1]["etf_name"]
        close_price = df["close_price"].astype(float)
        current_price = close_price.iloc[-1]
        rsi6 = self._calc_rsi(close_price, 6).iloc[-1]
        rsi12 = self._calc_rsi(close_price, 12).iloc[-1]
        rsi24 = self._calc_rsi(close_price, 24).iloc[-1]
        score, level, signal = self._evaluate(rsi6)
        return {
            "etf_code": etf_code,
            "etf_name": etf_name,
            "current_price": round(current_price, 3),
            "rsi6": round(rsi6, 2) if pd.notna(rsi6) else None,
            "rsi12": round(rsi12, 2) if pd.notna(rsi12) else None,
            "rsi24": round(rsi24, 2) if pd.notna(rsi24) else None,
            "score": score,
            "level": level,
            "signal": signal,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _evaluate(self, rsi):
        if pd.isna(rsi):
            return 0, "D", "无数据"
        if rsi < 20:
            return 100, "S", "强烈加仓"
        elif rsi < 30:
            return 90, "A", "加仓"
        elif rsi < 40:
            return 70, "B", "关注"
        elif rsi < 60:
            return 50, "C", "中性"
        elif rsi < 70:
            return 30, "C", "谨慎"
        elif rsi < 80:
            return 10, "D", "停止加仓"
        else:
            return 0, "D", "超买"

    def load(self):
        """Load: 写入 dwd_rsi_factor"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_rsi_factor")
        self.result_df.to_sql("dwd_rsi_factor", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        df = self.result_df.sort_values("score", ascending=False)
        print()
        print("=" * 100)
        print("RSI评分排行榜")
        print("=" * 100)
        for _, row in df.iterrows():
            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10} "
                f"RSI6:{row['rsi6']:>6} "
                f"得分:{row['score']:>3} "
                f"等级:{row['level']} "
                f"信号:{row['signal']}"
            )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    RSIFactorEngine().run()
