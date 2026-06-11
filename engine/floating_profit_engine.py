import sqlite3
import pandas as pd

from datetime import datetime


class FloatingProfitEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    # ==================================================
    # 获取持仓
    # ==================================================
    def load_position(self):

        conn = sqlite3.connect(self.db_path)

        sql = """
        select
            etf_code,
            etf_name,
            quantity,
            avg_cost
        from dwd_position
        """

        df = pd.read_sql(sql, conn)

        conn.close()

        return df

    # ==================================================
    # 获取行情
    # ==================================================
    def load_market_price(self):

        conn = sqlite3.connect(self.db_path)

        sql = """
        select
            etf_code,
            current_price
        from ods_market_price
        """

        df = pd.read_sql(sql, conn)

        conn.close()

        return df

    # ==================================================
    # 计算浮盈
    # ==================================================
    def calculate(self):

        position_df = self.load_position()

        market_df = self.load_market_price()

        df = pd.merge(
            position_df,
            market_df,
            on="etf_code",
            how="left"
        )

        # --------------------------
        # 缺失行情检查
        # --------------------------

        miss_df = df[
            df["current_price"].isna()
        ]

        if len(miss_df) > 0:

            print()
            print("缺失行情：")

            print(
                miss_df[
                    [
                        "etf_code",
                        "etf_name"
                    ]
                ]
            )

        # --------------------------
        # 核心计算
        # --------------------------

        df["cost_value"] = (
            df["quantity"]
            * df["avg_cost"]
        )

        df["market_value"] = (
            df["quantity"]
            * df["current_price"]
        )

        df["floating_profit"] = (
            df["market_value"]
            - df["cost_value"]
        )

        df["floating_profit_pct"] = (
            df["floating_profit"]
            / df["cost_value"]
            * 100
        )

        df["floating_profit_pct"] = (
            df["floating_profit_pct"]
            .round(2)
        )

        df["floating_profit"] = (
            df["floating_profit"]
            .round(2)
        )

        df["cost_value"] = (
            df["cost_value"]
            .round(2)
        )

        df["market_value"] = (
            df["market_value"]
            .round(2)
        )

        df["update_time"] = (
            datetime.now()
            .strftime("%Y-%m-%d %H:%M:%S")
        )

        return df

    # ==================================================
    # 保存结果
    # ==================================================
    def save_result(self, df):

        conn = sqlite3.connect(
            self.db_path
        )

        conn.execute(
            """
            DELETE FROM dwd_floating_profit
            """
        )

        df.to_sql(
            "dwd_floating_profit",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # ==================================================
    # 打印结果
    # ==================================================
    def print_result(self, df):

        print()

        print("=" * 100)

        print("浮盈浮亏分析")

        print("=" * 100)

        df = df.sort_values(
            "floating_profit",
            ascending=False
        )

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

        total_profit = (
            total_market
            - total_cost
        )

        total_pct = (
            total_profit
            / total_cost
            * 100
        )

        print("=" * 100)

        print("账户汇总")

        print("=" * 100)

        print(
            f"成本市值：{total_cost:,.2f}"
        )

        print(
            f"当前市值：{total_market:,.2f}"
        )

        print(
            f"浮动收益：{total_profit:,.2f}"
        )

        print(
            f"收益率：{total_pct:.2f}%"
        )

    # ==================================================
    # 主程序
    # ==================================================
    def run(self):

        df = self.calculate()

        self.save_result(df)

        self.print_result(df)


if __name__ == "__main__":

    FloatingProfitEngine().run()