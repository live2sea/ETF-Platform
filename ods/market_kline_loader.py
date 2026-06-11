# -*- coding: utf-8 -*-
import time
import sqlite3
import pandas as pd
import akshare as ak
from datetime import datetime


class MarketKlineLoader:

    def __init__(self):
        self.db_path = "data/etf.db"
        self.max_retries = 3
        self.request_delay = 1.5

    def load_position_etf(self):
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql(
                "SELECT etf_code, etf_name FROM dwd_position WHERE quantity > 0",
                conn
            )
        finally:
            conn.close()

        if df.empty:
            return df

        df["etf_code"] = df["etf_code"].astype(str).str.strip()
        return df

    def _fetch_kline(self, etf_code):
        prefix = "sh" if etf_code.startswith(("5", "6")) else "sz"
        symbol = f"{prefix}{etf_code}"

        df = ak.fund_etf_hist_sina(symbol=symbol)
        if df is None or df.empty:
            return None

        df = df.rename(columns={
            "date": "trade_date",
            "open": "open_price",
            "high": "high_price",
            "low": "low_price",
            "close": "close_price",
            "volume": "volume",
        })

        df["amount"] = 0.0
        df["etf_code"] = etf_code
        df["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return df[[
            "etf_code", "trade_date",
            "open_price", "high_price", "low_price",
            "close_price", "volume",
            "amount", "update_time"
        ]]

    def load_single_kline(self, etf_code, etf_name, retry=0):
        try:
            print(f"下载 {etf_code} {etf_name}" + (f" (重试{retry})" if retry > 0 else ""))

            df = self._fetch_kline(etf_code)
            if df is None or df.empty:
                return None

            df["etf_name"] = etf_name
            return df

        except Exception as e:
            print(f"下载失败 {etf_code}: {type(e).__name__}: {e}")

            if retry < self.max_retries:
                wait = self.request_delay * (2 ** retry)
                print(f"等待 {wait:.1f}s 重试...")
                time.sleep(wait)
                return self.load_single_kline(etf_code, etf_name, retry + 1)

            return None

    def save_result(self, result):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("DELETE FROM ods_market_kline")
            result.to_sql("ods_market_kline", conn, if_exists="append", index=False)
            conn.commit()
        finally:
            conn.close()

    def run(self):
        etf_df = self.load_position_etf()

        if etf_df.empty:
            print("无持仓ETF")
            return

        print("=" * 80)
        print("开始下载ETF历史K线")
        print("=" * 80)

        all_data = []

        for _, row in etf_df.iterrows():
            time.sleep(self.request_delay)

            df = self.load_single_kline(row["etf_code"], row["etf_name"])
            if df is not None:
                all_data.append(df)

        if not all_data:
            print("无数据 — 所有 ETF 均下载失败")
            return

        result = pd.concat(all_data, ignore_index=True)

        self.save_result(result)

        print("=" * 80)
        print("下载完成")
        print("=" * 80)
        print(f"ETF数量: {etf_df.shape[0]}")
        print(f"K线总数: {len(result)}")

        min_date = result["trade_date"].min()
        max_date = result["trade_date"].max()
        print(f"覆盖日期: {min_date} ~ {max_date}")


if __name__ == "__main__":
    MarketKlineLoader().run()