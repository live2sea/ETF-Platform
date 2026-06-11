# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
from datetime import datetime


class DrawdownEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    # ==================================================
    # K线读取
    # ==================================================
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

    # ==================================================
    # 单ETF计算
    # ==================================================
    def build_single(self, df):

        df = df.sort_values("trade_date")

        etf_code = df.iloc[-1]["etf_code"]
        etf_name = df.iloc[-1]["etf_name"]

        close_series = df["close_price"].astype(float)

        current_price = float(close_series.iloc[-1])

        # 最近252交易日 ≈ 52周
        lookback_df = df.tail(252)

        high_52w = float(
            lookback_df["close_price"].max()
        )

        low_52w = float(
            lookback_df["close_price"].min()
        )

        drawdown_pct = (
            (current_price - high_52w)
            / high_52w
            * 100
        )

        score, level, signal = self.evaluate(
            drawdown_pct
        )

        return {
            "etf_code": etf_code,
            "etf_name": etf_name,

            "current_price":
                round(current_price, 3),

            "high_52w":
                round(high_52w, 3),

            "low_52w":
                round(low_52w, 3),

            "drawdown_pct":
                round(drawdown_pct, 2),

            "score": score,

            "level": level,

            "signal": signal,

            "update_time":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        }

    # ==================================================
    # 回撤评分
    # ==================================================
    def evaluate(self, drawdown):

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

    # ==================================================
    # 全量计算
    # ==================================================
    def build_factor(self, df):

        result = []

        for code, group in df.groupby("etf_code"):

            if len(group) < 30:
                continue

            result.append(
                self.build_single(group)
            )

        return pd.DataFrame(result)

    # ==================================================
    # 保存
    # ==================================================
    def save_result(self, result):

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            "DELETE FROM dwd_drawdown_factor"
        )

        result.to_sql(
            "dwd_drawdown_factor",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # ==================================================
    # 输出
    # ==================================================
    def print_result(self, result):

        result = result.sort_values(
            "drawdown_pct"
        )

        print()
        print("=" * 100)
        print("52周回撤排行榜")
        print("=" * 100)

        for _, row in result.iterrows():

            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10} "
                f"回撤:{row['drawdown_pct']:>7}% "
                f"等级:{row['level']} "
                f"信号:{row['signal']}"
            )

    # ==================================================
    # 主流程
    # ==================================================
    def run(self):

        df = self.load_kline()

        result = self.build_factor(df)

        self.save_result(result)

        self.print_result(result)


if __name__ == "__main__":

    DrawdownEngine().run()