#!/usr/bin/env python3
# 解释：该脚本定义了一个FloatingProfitEngine类，用于计算ETF的浮动盈亏。
# 它从SQLite数据库中加载持仓和行情数据，计算每只ETF的浮动盈亏，并将结果保存到数据库中的浮动盈亏表中。
# 最后，在主程序中创建一个FloatingProfitEngine实例，执行计算并打印分析结果。

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class FloatingProfitEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 加载持仓与行情数据"""
        conn = sqlite3.connect(self.db_path)

        self.position_df = pd.read_sql(
            """
            select etf_code, etf_name, quantity, avg_cost
            from dwd_position
            """,
            conn,
        )

        self.market_df = pd.read_sql(
            """
            select etf_code, current_price
            from ods_market_price
            """,
            conn,
        )

        conn.close()

    def transform(self):
        """Transform: 合并持仓与行情，计算浮动盈亏"""
        df = pd.merge(self.position_df, self.market_df, on="etf_code", how="left")

        # 缺失行情检查
        miss_df = df[df["current_price"].isna()]
        if len(miss_df) > 0:
            print()
            print("缺失行情：")
            print(miss_df[["etf_code", "etf_name"]])

        # 核心计算
        df["cost_value"] = df["quantity"] * df["avg_cost"]
        df["market_value"] = df["quantity"] * df["current_price"]
        df["floating_profit"] = df["market_value"] - df["cost_value"]
        df["floating_profit_pct"] = (df["floating_profit"] / df["cost_value"] * 100).round(2)
        df["floating_profit"] = df["floating_profit"].round(2)
        df["cost_value"] = df["cost_value"].round(2)
        df["market_value"] = df["market_value"].round(2)
        df["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.result_df = df

    def load(self):
        """Load: 写入 dwd_floating_profit"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_floating_profit")
        self.result_df.to_sql("dwd_floating_profit", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        """打印浮动盈亏分析报告"""
        df = self.result_df.sort_values("floating_profit", ascending=False)

        print()
        print("=" * 100)
        print("浮盈浮亏分析")
        print("=" * 100)

        for _, row in df.iterrows():
            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10} "
                f"持仓:{int(row['quantity']):>7} "
                f"成本:{row['avg_cost']:>6.3f} "
                f"现价:{row['current_price']:>6.3f} "
                f"浮盈:{row['floating_profit']:>10.2f} "
                f"收益率:{row['floating_profit_pct']:>7.2f}%"
            )

        print()

        total_cost = df["cost_value"].sum()
        total_market = df["market_value"].sum()
        total_profit = total_market - total_cost
        total_pct = total_profit / total_cost * 100

        print("=" * 100)
        print("账户汇总")
        print("=" * 100)
        print(f"成本市值：{total_cost:,.2f}")
        print(f"当前市值：{total_market:,.2f}")
        print(f"浮动收益：{total_profit:,.2f}")
        print(f"收益率：{total_pct:.2f}%")

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    FloatingProfitEngine().run()
