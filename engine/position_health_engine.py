# -*- coding:utf-8 -*-

import sqlite3
import pandas as pd
from datetime import datetime


class PositionHealthEngine:

    def __init__(self):
        self.db_path = "data/etf.db"

    def load_data(self):

        conn = sqlite3.connect(self.db_path)

        allocation = pd.read_sql(
            """
            select *
            from dwd_allocation
            """,
            conn
        )

        category = pd.read_sql(
            """
            select *
            from dwd_category_allocation
            """,
            conn
        )

        conn.close()

        return allocation, category

    def check_single_etf(self, allocation):

        max_row = allocation.loc[
            allocation["allocation_pct"].idxmax()
        ]

        pct = float(max_row["allocation_pct"])

        if pct > 30:
            level = "危险"
            suggestion = "立即降低单ETF仓位"
        elif pct > 20:
            level = "偏高"
            suggestion = "暂停加仓"
        else:
            level = "正常"
            suggestion = "继续持有"

        return {
            "health_item": "最大单ETF仓位",
            "item_value": pct,
            "risk_level": level,
            "suggestion": suggestion
        }

    def check_category(self, category):

        max_row = category.loc[
            category["allocation_pct"].idxmax()
        ]

        pct = float(max_row["allocation_pct"])

        name = max_row["category_name"]

        if pct > 40:
            level = "危险"
            suggestion = f"{name}仓位过高"
        elif pct > 25:
            level = "注意"
            suggestion = f"{name}仓位偏高"
        else:
            level = "正常"
            suggestion = "配置合理"

        return {
            "health_item": f"主题集中度({name})",
            "item_value": pct,
            "risk_level": level,
            "suggestion": suggestion
        }

    def check_etf_count(self, allocation):

        count = len(allocation)

        if count > 20:
            level = "危险"
            suggestion = "ETF数量过多"
        elif count > 15:
            level = "注意"
            suggestion = "持仓略分散"
        else:
            level = "正常"
            suggestion = "持仓数量合理"

        return {
            "health_item": "ETF数量",
            "item_value": count,
            "risk_level": level,
            "suggestion": suggestion
        }

    def check_overlap(self, allocation):

        nasdaq_group = [
            "159632",
            "159696",
            "159659",
            "513110",
            "513300"
        ]

        overlap = allocation[
            allocation["etf_code"].isin(nasdaq_group)
        ]

        count = len(overlap)

        if count >= 4:
            level = "危险"
            suggestion = "纳指ETF重复严重"
        elif count >= 3:
            level = "注意"
            suggestion = "存在重复持仓"
        else:
            level = "正常"
            suggestion = "无明显重叠"

        return {
            "health_item": "纳指ETF重叠",
            "item_value": count,
            "risk_level": level,
            "suggestion": suggestion
        }

    def save_result(self, df):

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dwd_position_health
            (
                health_item TEXT PRIMARY KEY,
                item_value REAL,
                risk_level TEXT,
                suggestion TEXT,
                update_time TEXT
            )
            """
        )

        conn.execute("DELETE FROM dwd_position_health")

        df.to_sql(
            "dwd_position_health",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()
        conn.close()

    def run(self):

        allocation, category = self.load_data()

        result = []

        result.append(
            self.check_single_etf(allocation)
        )

        result.append(
            self.check_category(category)
        )

        result.append(
            self.check_etf_count(allocation)
        )

        result.append(
            self.check_overlap(allocation)
        )

        df = pd.DataFrame(result)

        df["update_time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.save_result(df)

        print("\n")
        print("=" * 100)
        print("组合健康度分析")
        print("=" * 100)

        print(
            df[
                [
                    "health_item",
                    "item_value",
                    "risk_level",
                    "suggestion"
                ]
            ]
        )


if __name__ == "__main__":
    PositionHealthEngine().run()