# -*- coding:utf-8 -*-

import sqlite3
import pandas as pd
from datetime import datetime


class ETFOverlapEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

        self.etf_group = {

            "纳斯达克100": [
                "159632",
                "159696",
                "159659",
                "513110",
                "513300"
            ],

            "港股科技": [
                "159740",
                "513580",
                "513980"
            ],

            "日本": [
                "513000",
                "513800"
            ],

            "红利": [
                "510880",
                "563020"
            ]
        }

    def load_allocation(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                etf_code,
                etf_name,
                market_value,
                allocation_pct
            FROM dwd_allocation
            """,
            conn
        )

        conn.close()

        return df

    def calc_risk_level(
        self,
        etf_count,
        allocation_pct
    ):

        if etf_count >= 4:
            return "危险"

        if etf_count >= 3 and allocation_pct > 10:
            return "危险"

        if etf_count >= 2:
            return "注意"

        return "正常"

    def build_overlap(self, df):

        result = []

        total_value = df["market_value"].sum()

        for group_name, codes in self.etf_group.items():

            group_df = df[
                df["etf_code"].isin(codes)
            ]

            if group_df.empty:
                continue

            etf_count = len(group_df)

            group_value = group_df[
                "market_value"
            ].sum()

            allocation_pct = round(
                group_value / total_value * 100,
                2
            )

            risk_level = self.calc_risk_level(
                etf_count,
                allocation_pct
            )

            if risk_level == "危险":
                suggestion = "建议合并持仓"
            elif risk_level == "注意":
                suggestion = "控制新增仓位"
            else:
                suggestion = "保持"

            result.append({

                "group_name":
                    group_name,

                "etf_count":
                    etf_count,

                "total_value":
                    round(group_value, 2),

                "allocation_pct":
                    allocation_pct,

                "risk_level":
                    risk_level,

                "suggestion":
                    suggestion
            })

        return pd.DataFrame(result)

    def save_result(self, df):

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            dwd_etf_overlap
            (
                group_name TEXT,

                etf_count INTEGER,

                total_value REAL,

                allocation_pct REAL,

                risk_level TEXT,

                suggestion TEXT,

                update_time TEXT
            )
            """
        )

        conn.execute(
            "DELETE FROM dwd_etf_overlap"
        )

        df.to_sql(
            "dwd_etf_overlap",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()
        conn.close()

    def run(self):

        df = self.load_allocation()

        result = self.build_overlap(df)

        result["update_time"] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        self.save_result(result)

        print()
        print("=" * 100)
        print("ETF重叠分析")
        print("=" * 100)

        for _, row in result.iterrows():

            print(
                f"{row['group_name']:10}"
                f" ETF数:{row['etf_count']:2}"
                f" 占比:{row['allocation_pct']:6.2f}%"
                f" 风险:{row['risk_level']}"
                f" 建议:{row['suggestion']}"
            )


if __name__ == "__main__":
    ETFOverlapEngine().run()