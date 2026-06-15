import sqlite3
import pandas as pd

from datetime import datetime


class AllocationEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    # ==========================================
    # 持仓
    # ==========================================
    def load_position(self):

        conn = sqlite3.connect(
            self.db_path
        )

        sql = """
        select
            etf_code,
            etf_name,
            quantity,
            avg_cost
        from dwd_position
        """

        df = pd.read_sql(
            sql,
            conn
        )

        conn.close()

        df["etf_code"] = (
            df["etf_code"]
            .astype(str)
            .str.strip()
        )

        return df

    # ==========================================
    # 行情
    # ==========================================
    def load_market(self):

        conn = sqlite3.connect(
            self.db_path
        )

        sql = """
        select
            etf_code,
            current_price
        from ods_market_price
        """

        df = pd.read_sql(
            sql,
            conn
        )

        conn.close()

        df["etf_code"] = (
            df["etf_code"]
            .astype(str)
            .str.strip()
        )

        df["current_price"] = pd.to_numeric(
            df["current_price"],
            errors="coerce"
        )

        return df

    # ==========================================
    # 构建仓位
    # ==========================================
    def build_allocation(self):

        position_df = self.load_position()

        market_df = self.load_market()

        df = pd.merge(
            position_df,
            market_df,
            on="etf_code",
            how="left"
        )

        # --------------------------
        # 缺失行情检查
        # --------------------------

        missing_df = df[
            df["current_price"].isna()
        ]

        if len(missing_df) > 0:

            print()
            print("=" * 80)
            print("缺失行情")
            print("=" * 80)

            print(
                missing_df[
                    [
                        "etf_code",
                        "etf_name"
                    ]
                ]
            )

        # --------------------------
        # 计算成本市值
        # --------------------------

        df["cost_value"] = (
            df["quantity"]
            * df["avg_cost"]
        )

        # --------------------------
        # 计算实时市值
        # --------------------------

        df["market_value"] = (
            df["quantity"]
            * df["current_price"]
        )

        total_market_value = (
            df["market_value"]
            .sum()
        )

        if total_market_value <= 0:

            raise ValueError(
                f"总市值异常:{total_market_value}"
            )

        # --------------------------
        # 仓位占比
        # --------------------------

        df["allocation_pct"] = round(
            (
                df["market_value"]
                / total_market_value
                * 100
            ),
            2
        )

        df["update_time"] = (
            datetime.now()
            .strftime("%Y-%m-%d %H:%M:%S")
        )

        return df

    # ==========================================
    # 保存
    # ==========================================
    def save_result(self, df):

        conn = sqlite3.connect(
            self.db_path
        )

        conn.execute(
            """
            DELETE FROM dwd_allocation
            """
        )

        df.to_sql(
            "dwd_allocation",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # ==========================================
    # 输出
    # ==========================================
    def print_result(self, df):

        print()

        print("=" * 90)
        print("实时仓位结构分析")
        print("=" * 90)

        total_market_value = (
            df["market_value"]
            .sum()
        )

        print(
            f"总持仓市值：{total_market_value:,.2f}"
        )

        print()

        df = df.sort_values(
            "allocation_pct",
            ascending=False
        )

        for _, row in df.iterrows():

            print(
                f"{row['etf_code']} "
                f"{row['etf_name']:<10} "
                f"持仓:{int(row['quantity']):>7} "
                f"市值:{row['market_value']:>12.2f} "
                f"占比:{row['allocation_pct']:>6.2f}%"
            )

    # ==========================================
    # 主程序
    # ==========================================
    def run(self):

        df = self.build_allocation()

        self.save_result(df)

        self.print_result(df)


if __name__ == "__main__":

    AllocationEngine().run()