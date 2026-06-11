# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
from datetime import datetime


class AddPositionEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    # ==========================================
    # 加载综合信号
    # ==========================================
    def load_signal(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                etf_code,
                etf_name,
                signal_score
            FROM dwd_etf_signal
            """,
            conn
        )

        conn.close()

        return df

    # ==========================================
    # 加载仓位
    # ==========================================
    def load_allocation(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                etf_code,
                allocation_pct
            FROM dwd_allocation
            """,
            conn
        )

        conn.close()

        return df

    # ==========================================
    # 加载浮盈浮亏
    # ==========================================
    def load_floating(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                etf_code,
                floating_profit_pct
            FROM dwd_floating_profit
            """,
            conn
        )

        conn.close()

        return df

    # ==========================================
    # 浮亏评分
    # ==========================================
    def calc_floating_score(self, pct):

        if pd.isna(pct):
            return 50

        if pct <= -15:
            return 100

        if pct <= -10:
            return 80

        if pct <= -5:
            return 60

        return 20

    # ==========================================
    # 仓位评分
    # ==========================================
    def calc_allocation_score(self, pct):

        if pd.isna(pct):
            return 50

        if pct > 20:
            return 0

        if pct > 15:
            return 30

        if pct > 10:
            return 70

        return 100

    # ==========================================
    # 建议金额
    # ==========================================
    def calc_amount(self, score):

        if score >= 80:
            return 5000

        if score >= 70:
            return 3000

        if score >= 60:
            return 2000

        return 0

    # ==========================================
    # 建议文字
    # ==========================================
    def build_advice(self, score):

        if score >= 80:
            return "优先加仓"

        if score >= 70:
            return "可以加仓"

        if score >= 60:
            return "小额试仓"

        return "暂不加仓"

    # ==========================================
    # 计算
    # ==========================================
    def build_result(self):

        signal_df = self.load_signal()

        allocation_df = self.load_allocation()

        floating_df = self.load_floating()

        df = signal_df.merge(
            allocation_df,
            on="etf_code",
            how="left"
        )

        df = df.merge(
            floating_df,
            on="etf_code",
            how="left"
        )

        df["floating_score"] = (
            df["floating_profit_pct"]
            .apply(self.calc_floating_score)
        )

        df["allocation_score"] = (
            df["allocation_pct"]
            .apply(self.calc_allocation_score)
        )

        df["final_score"] = (
            df["signal_score"] * 0.5
            + df["floating_score"] * 0.2
            + df["allocation_score"] * 0.3
        )

        df["final_score"] = (
            df["final_score"]
            .round(2)
        )

        df["recommend_amount"] = (
            df["final_score"]
            .apply(self.calc_amount)
        )

        df["recommendation"] = (
            df["final_score"]
            .apply(self.build_advice)
        )

        df["update_time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return df.sort_values(
            "final_score",
            ascending=False
        )

    # ==========================================
    # 保存
    # ==========================================
    def save_result(self, df):

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            "DELETE FROM dwd_add_position_signal"
        )

        df.to_sql(
            "dwd_add_position_signal",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # ==========================================
    # 打印
    # ==========================================
    def print_result(self, df):

        print()
        print("=" * 100)
        print("今日加仓建议")
        print("=" * 100)

        top_df = (
            df[df["recommend_amount"] > 0]
            .head(10)
        )

        for _, row in top_df.iterrows():

            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10}"
                f" 综合分:{row['final_score']:>6}"
                f" 建议金额:{int(row['recommend_amount']):>6}"
                f" 建议:{row['recommendation']}"
            )

    # ==========================================
    # 主入口
    # ==========================================
    def run(self):

        df = self.build_result()

        self.save_result(df)

        self.print_result(df)

        print()
        print(
            f"生成加仓建议 {len(df)} 条"
        )


if __name__ == "__main__":

    AddPositionEngine().run()