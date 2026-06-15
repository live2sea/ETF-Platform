# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
from datetime import datetime


class RiskEngine:

    def __init__(self):
        self.db_path = "data/etf.db"

    def load_data(self):

        conn = sqlite3.connect(self.db_path)

        allocation = pd.read_sql(
            """
            SELECT *
            FROM dwd_allocation
            """,
            conn
        )

        category = pd.read_sql(
            """
            SELECT *
            FROM dwd_category_allocation
            """,
            conn
        )

        conn.close()

        return allocation, category

    def build_risk(self):

        allocation, category = self.load_data()

        risk_rows = []

        score = 100

        # ETF集中度风险

        for _, row in allocation.iterrows():

            pct = float(row["allocation_pct"])

            if pct >= 20:

                level = "高"
                score -= 10

            elif pct >= 15:

                level = "中"

            else:

                level = "低"

            risk_rows.append([
                "ETF",
                row["etf_name"],
                round(pct, 2),
                level,
                "单ETF建议不超过15%"
            ])

        # 主题风险

        for _, row in category.iterrows():

            pct = float(row["allocation_pct"])

            if pct >= 40:

                level = "高"
                score -= 15

            elif pct >= 30:

                level = "中"

            else:

                level = "低"

            risk_rows.append([
                "主题",
                row["category_name"],
                round(pct, 2),
                level,
                "单主题建议不超过30%"
            ])

        result = pd.DataFrame(
            risk_rows,
            columns=[
                "risk_type",
                "risk_name",
                "risk_value",
                "risk_level",
                "suggestion"
            ]
        )

        result["update_time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return result, max(score, 0)

    def save_result(self, df):

        conn = sqlite3.connect(self.db_path)

        df.to_sql(
            "dwd_risk_analysis",
            conn,
            if_exists="replace",
            index=False
        )

        conn.close()

    def show_result(self, df, score):

        print()
        print("=" * 100)
        print("组合风险分析")
        print("=" * 100)

        print(f"风险评分：{score}")

        if score >= 80:
            level = "A"

        elif score >= 60:
            level = "B"

        elif score >= 40:
            level = "C"

        else:
            level = "D"

        print(f"风险等级：{level}")
        print()

        high_risk = df[df["risk_level"] == "高"]

        if not high_risk.empty:

            print("高风险项目")
            print("-" * 100)

            for _, row in high_risk.iterrows():

                print(
                    f"{row['risk_type']} "
                    f"{row['risk_name']} "
                    f"{row['risk_value']:.2f}%"
                )

    def run(self):

        df, score = self.build_risk()

        self.save_result(df)

        self.show_result(df, score)


if __name__ == "__main__":
    RiskEngine().run()