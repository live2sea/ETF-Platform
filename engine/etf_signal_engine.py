# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
from datetime import datetime


class ETFSignalEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    # ==================================================
    # 读取因子
    # ==================================================
    def load_factor(self):

        conn = sqlite3.connect(self.db_path)

        ma_df = pd.read_sql(
            """
            SELECT
                etf_code,
                etf_name,
                trend_score  AS ma_score
            FROM dwd_ma_factor
            """,
            conn
        )

        rsi_df = pd.read_sql(
            """
            SELECT
                etf_code,
                score AS rsi_score
            FROM dwd_rsi_factor
            """,
            conn
        )

        drawdown_df = pd.read_sql(
            """
            SELECT
                etf_code,
                score AS drawdown_score
            FROM dwd_drawdown_factor
            """,
            conn
        )

        conn.close()

        df = ma_df.merge(
            rsi_df,
            on="etf_code",
            how="left"
        )

        df = df.merge(
            drawdown_df,
            on="etf_code",
            how="left"
        )

        df.fillna(0, inplace=True)

        return df

    # ==================================================
    # 综合评分
    # ==================================================
    def calculate_score(self, row):

        score = (
            row["ma_score"] * 0.4
            + row["rsi_score"] * 0.3
            + row["drawdown_score"] * 0.3
        )

        return round(score, 2)

    # ==================================================
    # 信号等级
    # ==================================================
    def evaluate(self, score):

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

    # ==================================================
    # 构建
    # ==================================================
    def build_signal(self, df):

        df["signal_score"] = df.apply(
            self.calculate_score,
            axis=1
        )

        levels = df["signal_score"].apply(
            self.evaluate
        )

        df["level"] = levels.apply(
            lambda x: x[0]
        )

        df["suggestion"] = levels.apply(
            lambda x: x[1]
        )

        df["update_time"] = (
            datetime.now()
            .strftime("%Y-%m-%d %H:%M:%S")
        )

        return df

    # ==================================================
    # 保存
    # ==================================================
    def save_result(self, df):

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            "DELETE FROM dwd_etf_signal"
        )

        df.to_sql(
            "dwd_etf_signal",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # ==================================================
    # 输出
    # ==================================================
    def print_result(self, df):

        df = df.sort_values(
            "signal_score",
            ascending=False
        )

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

    # ==================================================
    # 主流程
    # ==================================================
    def run(self):

        df = self.load_factor()

        result = self.build_signal(df)

        self.save_result(result)

        self.print_result(result)


if __name__ == "__main__":

    ETFSignalEngine().run()