# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
from datetime import datetime


class DashboardEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    def load_profit(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT *
            FROM dwd_floating_profit
            """,
            conn
        )

        conn.close()

        return df

    def load_category(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT *
            FROM dwd_category_allocation
            ORDER BY allocation_pct DESC
            """,
            conn
        )

        conn.close()

        return df

    def load_signal(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT *
            FROM dwd_etf_signal
            ORDER BY signal_score DESC
            """,
            conn
        )

        conn.close()

        return df

    def load_add_position(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT *
            FROM dwd_add_position_signal
            ORDER BY final_score DESC
            """,
            conn
        )

        conn.close()

        return df

    def load_risk(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT *
            FROM dwd_risk_analysis
            """,
            conn
        )

        conn.close()

        return df

    def load_rebalance(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT *
            FROM dwd_rebalance_v2
            ORDER BY ABS(deviation_pct) DESC
            """,
            conn
        )

        conn.close()

        return df

    def build_dashboard(self):

        profit_df = self.load_profit()
        category_df = self.load_category()
        signal_df = self.load_signal()
        add_df = self.load_add_position()
        risk_df = self.load_risk()
        rebalance_df = self.load_rebalance()

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        rows = []

        # ==========================
        # 账户总览
        # ==========================

        total_cost = round(
            profit_df["cost_value"].sum(),
            2
        )

        total_market = round(
            profit_df["market_value"].sum(),
            2
        )

        total_profit = round(
            profit_df["floating_profit"].sum(),
            2
        )

        profit_pct = round(
            total_profit /
            total_cost * 100,
            2
        )

        rows.extend([

            ["总成本", str(total_cost), now],

            ["总市值", str(total_market), now],

            ["总盈亏", str(total_profit), now],

            ["收益率", f"{profit_pct}%", now]

        ])

        # ==========================
        # 第一重仓主题
        # ==========================

        if not category_df.empty:

            top1 = category_df.iloc[0]

            rows.append([

                "第一重仓",

                f"{top1['category_name']} "
                f"{top1['allocation_pct']:.2f}%",

                now

            ])

        # ==========================
        # 最佳ETF
        # ==========================

        best_signal = signal_df.iloc[0]

        rows.append([

            "最佳ETF",

            f"{best_signal['etf_code']} "
            f"{best_signal['etf_name']} "
            f"{best_signal['signal_score']}",

            now

        ])

        # ==========================
        # 推荐加仓
        # ==========================

        add_df = add_df[
            add_df["recommend_amount"] > 0
        ]

        if not add_df.empty:

            top_add = add_df.iloc[0]

            rows.append([

                "推荐加仓",

                f"{top_add['etf_code']} "
                f"{top_add['etf_name']} "
                f"{top_add['recommend_amount']:.0f}",

                now

            ])

        # ==========================
        # 风险提示
        # ==========================

        if not risk_df.empty:

            high_risk = risk_df[
                risk_df["risk_level"] == "高"
            ]

            rows.append([

                "高风险项数量",

                str(len(high_risk)),

                now

            ])

        # ==========================
        # 再平衡重点
        # ==========================

        if not rebalance_df.empty:

            top_dev = rebalance_df.iloc[0]

            rows.append([

                "偏离最大仓位",

                f"{top_dev['category']} "
                f"{top_dev['deviation_pct']:.2f}%",

                now

            ])

        dashboard_df = pd.DataFrame(

            rows,

            columns=[
                "item_name",
                "item_value",
                "update_time"
            ]
        )

        return dashboard_df

    def save_result(self, result):

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            "DELETE FROM dwd_dashboard"
        )

        result.to_sql(

            "dwd_dashboard",

            conn,

            if_exists="append",

            index=False

        )

        conn.commit()

        conn.close()

    def run(self):

        result = self.build_dashboard()

        self.save_result(result)

        print()

        print("=" * 100)
        print("ETF驾驶舱")
        print("=" * 100)

        for _, row in result.iterrows():

            print(
                f"{row['item_name']:<15}"
                f"{row['item_value']}"
            )


if __name__ == "__main__":

    DashboardEngine().run()