#!/usr/bin/env python3
#解释：该脚本定义了一个PositionCalculator类，用于计算ETF的持仓情况。它从SQLite数据库中加载交易记录数据，计算每个ETF的持仓数量、买入金额和卖出金额，并打印当前持仓情况。

import sqlite3
import pandas as pd


class PositionCalculator:

    def __init__(self):

        self.db_path = "data/etf.db"

    def load_trade_data(self):

        conn = sqlite3.connect(
            self.db_path
        )

        df = pd.read_sql(
            """
            SELECT *
            FROM ods_trade_record
            ORDER BY trade_date,trade_time
            """,
            conn
        )

        conn.close()

        return df

    def calculate(self):

        df = self.load_trade_data()

        positions = {}

        for _, row in df.iterrows():

            code = row["etf_code"]

            if code not in positions:

                positions[code] = {
                    "name": row["etf_name"],
                    "qty": 0,
                    "buy_amount": 0,
                    "sell_amount": 0
                }

            if row["trade_type"] == "买入":

                positions[code]["qty"] += row["quantity"]

                positions[code]["buy_amount"] += (
                    row["quantity"] *
                    row["price"]
                    + row["fee"]
                )

            elif row["trade_type"] == "卖出":

                positions[code]["qty"] -= row["quantity"]

                positions[code]["sell_amount"] += (
                    row["quantity"] *
                    row["price"]
                    - row["fee"]
                )

        return positions


if __name__ == "__main__":

    calc = PositionCalculator()

    positions = calc.calculate()

    print()

    print("===== 当前持仓 =====")

    for code, pos in positions.items():

        if pos["qty"] > 0:

            print(
                f"{code}"
                f" {pos['name']}"
                f" 持仓:{pos['qty']}"
            )