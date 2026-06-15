#!/usr/bin/env python3
# 解释：该脚本定义了一个CostEngine类，用于计算ETF的持仓成本和盈亏情况。
# 它从SQLite数据库中加载交易记录数据，计算每个ETF的持仓数量、平均成本、买入金额、卖出金额和已实现盈亏，
# 并将计算结果保存到数据库中的持仓快照表中。最后，在主程序中创建一个CostEngine实例，执行计算并打印当前持仓情况。

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

# 将项目根目录加入 sys.path，使直接运行脚本时也能正常 import engine.*
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class CostEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 从 ods_trade_record 加载交易记录"""
        conn = sqlite3.connect(self.db_path)
        self.trade_df = pd.read_sql(
            """
            SELECT *
            FROM ods_trade_record
            ORDER BY trade_date, trade_time
            """,
            conn,
        )
        conn.close()

    def transform(self):
        """Transform: 逐笔计算持仓成本与已实现盈亏"""
        df = self.trade_df
        self.positions = {}

        for _, row in df.iterrows():
            code = row["etf_code"]

            if code not in self.positions:
                self.positions[code] = {
                    "name": row["etf_name"],
                    "quantity": 0,
                    "total_cost": 0,
                    "avg_cost": 0,
                    "buy_amount": 0,
                    "sell_amount": 0,
                    "realized_profit": 0,
                }

            p = self.positions[code]
            qty = int(row["quantity"])
            price = float(row["price"])
            fee = float(row["fee"])

            if row["trade_type"] == "买入":
                buy_cost = qty * price + fee
                p["quantity"] += qty
                p["total_cost"] += buy_cost
                p["buy_amount"] += buy_cost
                p["avg_cost"] = p["total_cost"] / p["quantity"]

            elif row["trade_type"] == "卖出":
                if p["quantity"] <= 0:
                    continue

                sell_amount = qty * price - fee
                cost_amount = qty * p["avg_cost"]
                profit = sell_amount - cost_amount

                p["realized_profit"] += profit
                p["sell_amount"] += sell_amount
                p["quantity"] -= qty
                p["total_cost"] -= cost_amount

                if p["quantity"] > 0:
                    p["avg_cost"] = p["total_cost"] / p["quantity"]
                else:
                    p["avg_cost"] = 0
                    p["total_cost"] = 0

    def load(self):
        """Load: 将持仓快照写入 dwd_position"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_position")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows = []
        for code, p in self.positions.items():
            if p["quantity"] <= 0:
                continue
            rows.append(
                [
                    code,
                    p["name"],
                    p["quantity"],
                    round(p["avg_cost"], 4),
                    round(p["buy_amount"], 2),
                    round(p["sell_amount"], 2),
                    round(p["realized_profit"], 2),
                    now,
                ]
            )

        snapshot_df = pd.DataFrame(
            rows,
            columns=[
                "etf_code",
                "etf_name",
                "quantity",
                "avg_cost",
                "buy_amount",
                "sell_amount",
                "realized_profit",
                "update_time",
            ],
        )

        snapshot_df.to_sql(
            "dwd_position", conn, if_exists="append", index=False
        )
        conn.commit()
        conn.close()

        print(f"持仓快照写入成功：{len(snapshot_df)}条")


if __name__ == "__main__":
    engine = CostEngine()
    engine.run()

    print()
    print("===== 当前持仓 =====")

    for code, p in engine.positions.items():
        if p["quantity"] > 0:
            print(
                f"{code} {p['name']}"
                f" | 持仓:{p['quantity']}"
                f" | 成本:{p['avg_cost']:.4f}"
                f" | 已实现:{p['realized_profit']:.2f}"
            )
