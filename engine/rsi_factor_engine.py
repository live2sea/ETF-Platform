# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime


class RSIFactorEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    # ---------------------------------------------------
    # 获取K线
    # ---------------------------------------------------
    def load_kline(self):

        conn = sqlite3.connect(self.db_path)

        sql = """
        SELECT *
        FROM ods_market_kline
        ORDER BY etf_code, trade_date
        """

        df = pd.read_sql(sql, conn)

        conn.close()

        return df

    # ---------------------------------------------------
    # RSI计算
    # ---------------------------------------------------
    def calc_rsi(self, close_series, period=14):

        delta = close_series.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        return rsi

    # ---------------------------------------------------
    # 单ETF
    # ---------------------------------------------------
    def build_single(self, df):

        df = df.sort_values("trade_date")

        etf_code = df.iloc[-1]["etf_code"]

        etf_name = df.iloc[-1]["etf_name"]

        close_price = df["close_price"].astype(float)

        current_price = close_price.iloc[-1]

        rsi6 = self.calc_rsi(close_price, 6).iloc[-1]

        rsi12 = self.calc_rsi(close_price, 12).iloc[-1]

        rsi24 = self.calc_rsi(close_price, 24).iloc[-1]

        score, level, signal = self.evaluate(rsi6)

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

            "update_time":
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # ---------------------------------------------------
    # RSI评分
    # ---------------------------------------------------
    def evaluate(self, rsi):

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

    # ---------------------------------------------------
    # 全量计算
    # ---------------------------------------------------
    def build_factor(self, df):

        result = []

        for code, group in df.groupby("etf_code"):

            if len(group) < 30:
                continue

            row = self.build_single(group)

            result.append(row)

        return pd.DataFrame(result)

    # ---------------------------------------------------
    # 保存
    # ---------------------------------------------------
    def save_result(self, result):

        conn = sqlite3.connect(self.db_path)

        conn.execute("DELETE FROM dwd_rsi_factor")

        result.to_sql(
            "dwd_rsi_factor",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # ---------------------------------------------------
    # 输出
    # ---------------------------------------------------
    def print_result(self, result):

        result = result.sort_values(
            "score",
            ascending=False
        )

        print()
        print("=" * 100)
        print("RSI评分排行榜")
        print("=" * 100)

        for _, row in result.iterrows():

            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10} "
                f"RSI6:{row['rsi6']:>6} "
                f"得分:{row['score']:>3} "
                f"等级:{row['level']} "
                f"信号:{row['signal']}"
            )

    # ---------------------------------------------------
    # 主流程
    # ---------------------------------------------------
    def run(self):

        df = self.load_kline()

        result = self.build_factor(df)

        self.save_result(result)

        self.print_result(result)


if __name__ == "__main__":

    RSIFactorEngine().run()