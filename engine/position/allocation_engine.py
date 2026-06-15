#!/usr/bin/env python3
# 解释：该脚本定义了一个AllocationEngine类，用于计算ETF的实时仓位结构。
# 它从SQLite数据库中加载持仓和行情数据，计算每只ETF的市值占比，并将结果保存到数据库中的仓位分配表中。
# 最后，在主程序中创建一个AllocationEngine实例，执行计算并打印分析结果。

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class AllocationEngine(BaseEngine):

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

        self.position_df["etf_code"] = self.position_df["etf_code"].astype(str).str.strip()
        self.market_df["etf_code"] = self.market_df["etf_code"].astype(str).str.strip()
        self.market_df["current_price"] = pd.to_numeric(self.market_df["current_price"], errors="coerce")

    def transform(self):
        """Transform: 合并计算市值与仓位占比"""
        df = pd.merge(self.position_df, self.market_df, on="etf_code", how="left")

        # 缺失行情检查
        missing_df = df[df["current_price"].isna()]
        if len(missing_df) > 0:
            print()
            print("=" * 80)
            print("缺失行情")
            print("=" * 80)
            print(missing_df[["etf_code", "etf_name"]])

        # 计算市值
        df["cost_value"] = df["quantity"] * df["avg_cost"]
        df["market_value"] = df["quantity"] * df["current_price"]

        total_market_value = df["market_value"].sum()
        if total_market_value <= 0:
            raise ValueError(f"总市值异常:{total_market_value}")

        df["allocation_pct"] = round(df["market_value"] / total_market_value * 100, 2)
        df["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.result_df = df

    def load(self):
        """Load: 写入 dwd_allocation"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_allocation")
        self.result_df.to_sql("dwd_allocation", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        """打印实时仓位结构分析"""
        df = self.result_df.sort_values("allocation_pct", ascending=False)

        print()
        print("=" * 90)
        print("实时仓位结构分析")
        print("=" * 90)

        total_market_value = df["market_value"].sum()
        print(f"总持仓市值：{total_market_value:,.2f}")
        print()

        for _, row in df.iterrows():
            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10} "
                f"持仓:{int(row['quantity']):>7} "
                f"市值:{row['market_value']:>12.2f} "
                f"占比:{row['allocation_pct']:>6.2f}%"
            )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    AllocationEngine().run()
