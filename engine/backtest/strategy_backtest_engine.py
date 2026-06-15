# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class StrategyBacktestEngine(BaseEngine):

    def __init__(self):
        super().__init__()
        self.initial_cash = 100000

    def extract(self):
        """Extract: 加载K线和信号数据"""
        conn = sqlite3.connect(self.db_path)
        self.kline_df = pd.read_sql(
            "SELECT etf_code, etf_name, trade_date, close_price FROM ods_market_kline ORDER BY trade_date",
            conn,
        )
        self.signal_df = pd.read_sql(
            "SELECT etf_code, etf_name, signal_score FROM dwd_etf_signal",
            conn,
        )
        conn.close()

    def transform(self):
        """Transform: 逐只ETF回测"""
        results = []
        for _, signal in self.signal_df.iterrows():
            code = signal["etf_code"]
            name = signal["etf_name"]
            score = signal["signal_score"]
            df = self.kline_df[self.kline_df["etf_code"] == code]
            if len(df) < 50:
                continue
            results.append(self._backtest_etf(code, name, df, score))
        self.result_df = pd.DataFrame(results)

    def _backtest_etf(self, etf_code, etf_name, df, score):
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

        total_return = (cash - self.initial_cash) / self.initial_cash * 100
        win_rate = (win_count / trade_count * 100) if trade_count > 0 else 0

        return {
            "strategy_name": "Signal70",
            "etf_code": etf_code,
            "etf_name": etf_name,
            "trade_count": trade_count,
            "win_count": win_count,
            "win_rate": round(win_rate, 2),
            "total_return": round(total_return, 2),
            "annual_return": round(total_return / 3, 2),
            "max_drawdown": 0,
            "sharpe_ratio": 0,
        }

    def load(self):
        """Load: 写入 dwd_backtest_result"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_backtest_result")
        self.result_df["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.result_df.to_sql("dwd_backtest_result", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()
        print(f"\n[OK] 回测完成 {len(self.result_df)}个ETF")

    def print_result(self):
        print()
        print("=" * 80)
        print("策略回测")
        print("=" * 80)
        print(
            self.result_df[["etf_code", "etf_name", "total_return", "win_rate"]]
            .sort_values("total_return", ascending=False)
            .head(20)
        )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    StrategyBacktestEngine().run()
