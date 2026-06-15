# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd

from datetime import datetime


class StrategyBacktestEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

        self.initial_cash = 100000

    def load_data(self):

        conn = sqlite3.connect(
            self.db_path
        )

        kline = pd.read_sql(
            """
            SELECT
                etf_code,
                etf_name,
                trade_date,
                close_price
            FROM ods_market_kline
            ORDER BY trade_date
            """,
            conn
        )

        signal = pd.read_sql(
            """
            SELECT
                etf_code,
                etf_name,
                signal_score
            FROM dwd_etf_signal
            """,
            conn
        )

        conn.close()

        return kline, signal

    def backtest_etf(
        self,
        etf_code,
        etf_name,
        df,
        score
    ):

        cash = self.initial_cash

        position = 0

        trade_count = 0

        win_count = 0

        entry_price = 0

        for _, row in df.iterrows():

            price = row["close_price"]

            if score >= 70 and position == 0:

                position = cash / price

                cash = 0

                entry_price = price

                trade_count += 1

            elif score < 50 and position > 0:

                cash = position * price

                if price > entry_price:

                    win_count += 1

                position = 0

        if position > 0:

            cash = position * df.iloc[-1]["close_price"]

        total_return = (
            cash - self.initial_cash
        ) / self.initial_cash * 100

        win_rate = 0

        if trade_count > 0:

            win_rate = (
                win_count
                / trade_count
                * 100
            )

        return {

            "strategy_name":
                "Signal70",

            "etf_code":
                etf_code,

            "etf_name":
                etf_name,

            "trade_count":
                trade_count,

            "win_count":
                win_count,

            "win_rate":
                round(win_rate, 2),

            "total_return":
                round(total_return, 2),

            "annual_return":
                round(total_return / 3, 2),

            "max_drawdown":
                0,

            "sharpe_ratio":
                0
        }

    def run(self):

        print()

        print("=" * 80)
        print("策略回测")
        print("=" * 80)

        kline_df, signal_df = (
            self.load_data()
        )

        results = []

        for _, signal in signal_df.iterrows():

            code = signal["etf_code"]

            name = signal["etf_name"]

            score = signal["signal_score"]

            df = kline_df[
                kline_df["etf_code"] == code
            ]

            if len(df) < 50:
                continue

            result = self.backtest_etf(
                code,
                name,
                df,
                score
            )

            results.append(result)

        result_df = pd.DataFrame(
            results
        )

        self.save(
            result_df
        )

        print(
            result_df[
                [
                    "etf_code",
                    "etf_name",
                    "total_return",
                    "win_rate"
                ]
            ]
            .sort_values(
                "total_return",
                ascending=False
            )
            .head(20)
        )

    def save(self, df):

        conn = sqlite3.connect(
            self.db_path
        )

        conn.execute(
            """
            DELETE FROM
            dwd_backtest_result
            """
        )

        df["update_time"] = (
            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        df.to_sql(
            "dwd_backtest_result",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

        print()

        print(
            f"✓ 回测完成 {len(df)}个ETF"
        )


if __name__ == "__main__":

    StrategyBacktestEngine().run()