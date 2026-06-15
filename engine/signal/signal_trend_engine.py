# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd

from datetime import datetime


class SignalTrendEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    def load_history(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                trade_date,
                etf_code,
                etf_name,
                signal_score
            FROM dwd_signal_history
            ORDER BY trade_date
            """,
            conn
        )

        conn.close()

        return df

    def calculate(self):

        df = self.load_history()

        if df.empty:

            return pd.DataFrame()

        dates = sorted(
            df["trade_date"].unique()
        )

        if len(dates) < 2:

            print("历史数据不足2天")

            return pd.DataFrame()

        today = dates[-1]

        yesterday = dates[-2]

        today_df = df[
            df["trade_date"] == today
        ]

        yesterday_df = df[
            df["trade_date"] == yesterday
        ]

        result = today_df.merge(
            yesterday_df[
                [
                    "etf_code",
                    "signal_score"
                ]
            ],
            on="etf_code",
            how="left",
            suffixes=(
                "_today",
                "_yesterday"
            )
        )

        result.rename(
            columns={
                "signal_score_today":
                    "today_score",
                "signal_score_yesterday":
                    "yesterday_score"
            },
            inplace=True
        )

        result["yesterday_score"] = (
            result["yesterday_score"]
            .fillna(
                result["today_score"]
            )
        )

        result["change_score"] = (
            result["today_score"]
            -
            result["yesterday_score"]
        )

        def get_trend(x):

            if x >= 5:
                return "显著增强"

            elif x > 0:
                return "增强"

            elif x <= -5:
                return "显著走弱"

            elif x < 0:
                return "走弱"

            return "持平"

        result["trend"] = (
            result["change_score"]
            .apply(get_trend)
        )

        result["update_time"] = (
            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        return result[
            [
                "etf_code",
                "etf_name",
                "today_score",
                "yesterday_score",
                "change_score",
                "trend",
                "update_time"
            ]
        ]

    def save(self, df):

        if df.empty:
            return

        conn = sqlite3.connect(
            self.db_path
        )

        conn.execute(
            "DELETE FROM dwd_signal_trend"
        )

        df.to_sql(
            "dwd_signal_trend",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

        print(
            f"✓ 写入{len(df)}条趋势记录"
        )

    def run(self):

        print()
        print("=" * 80)
        print("ETF评分趋势分析")
        print("=" * 80)

        df = self.calculate()

        self.save(df)

        if not df.empty:

            print(
                df.sort_values(
                    "change_score",
                    ascending=False
                )
                .head(10)
            )


if __name__ == "__main__":

    SignalTrendEngine().run()