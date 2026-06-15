# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class MAFactorEngine(BaseEngine):
    """趋势因子引擎: MA20/MA60/MA120/MA250 趋势评分"""

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 加载K线"""
        conn = sqlite3.connect(self.db_path)
        self.kline_df = pd.read_sql(
            "SELECT * FROM ods_market_kline ORDER BY etf_code, trade_date",
            conn,
        )
        conn.close()

    def transform(self):
        """Transform: 计算每只ETF的MA趋势因子"""
        df = self.kline_df
        result = []
        for code in df["etf_code"].unique():
            tmp = df[df["etf_code"] == code]
            row = self._calc_single(tmp)
            score = self._calc_score(row)
            level, signal = self._get_level(score)
            result.append({
                "etf_code": row["etf_code"],
                "etf_name": row["etf_name"],
                "trade_date": row["trade_date"],
                "close_price": row["close_price"],
                "ma20": round(row["ma20"], 4),
                "ma60": round(row["ma60"], 4),
                "ma120": round(row["ma120"], 4),
                "ma250": round(row["ma250"], 4),
                "trend_score": score,
                "trend_level": level,
                "signal": signal,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        self.result_df = pd.DataFrame(result)

    def _calc_single(self, df):
        df = df.sort_values("trade_date")
        df["ma20"] = df["close_price"].rolling(20).mean()
        df["ma60"] = df["close_price"].rolling(60).mean()
        df["ma120"] = df["close_price"].rolling(120).mean()
        df["ma250"] = df["close_price"].rolling(250).mean()
        return df.iloc[-1]

    def _calc_score(self, row):
        score = 0
        close = row["close_price"]
        ma20, ma60, ma120, ma250 = row["ma20"], row["ma60"], row["ma120"], row["ma250"]
        if close > ma20:
            score += 10
        if close > ma60:
            score += 15
        if close > ma120:
            score += 20
        if close > ma250:
            score += 25
        if ma20 > ma60:
            score += 10
        if ma60 > ma120:
            score += 10
        if ma120 > ma250:
            score += 10
        return score

    def _get_level(self, score):
        if score >= 85:
            return "S", "加仓"
        elif score >= 70:
            return "A", "持有"
        elif score >= 50:
            return "B", "观察"
        elif score >= 30:
            return "C", "谨慎"
        else:
            return "D", "停止加仓"

    def load(self):
        """Load: 写入 dwd_ma_factor"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_ma_factor")
        self.result_df.to_sql("dwd_ma_factor", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        df = self.result_df.sort_values("trend_score", ascending=False)
        print()
        print("=" * 100)
        print("MA趋势评分")
        print("=" * 100)
        for _, row in df.iterrows():
            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:10s} "
                f"得分:{row['trend_score']:3d} "
                f"等级:{row['trend_level']} "
                f"信号:{row['signal']}"
            )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    MAFactorEngine().run()
