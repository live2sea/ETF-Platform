# -*- coding: utf-8 -*-
"""
Macro Loader -- AKShare 8       /
   -  ->  AKShare     ODS
   -  -> (indicator_date, indicator_name)    
   -  ->      ODS  WARN + traceback
"""

import sqlite3
import json
import os
import traceback
import pandas as pd
import akshare as ak
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "macro_weights.json")
DB_PATH = os.path.join(ROOT, "data", "etf.db")

INDICATOR_LOADERS = {
    "macro_china_pmi":                   "load_pmi",
    "macro_china_money_supply":          "load_m2",
    "macro_china_china_us_yield_spread": "load_yield_spread",
    "macro_china_cpi_yearly":            "load_cpi",
    "macro_china_ppi_yearly":            "load_ppi",
    "macro_usa_interest_rate":           "load_fed_rate",
    "stock_a_pe_csi300":                 "load_csi300_pe",
    "stock_hsgt_north_net_flow_in_em":   "load_north_flow",
}


class MacroLoader:

    def __init__(self):
        self.db_path = DB_PATH
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self._ensure_table()
        self._existing = self._load_existing_keys()

    # ================================================================ #
    # Table
    # ================================================================ #
    def _ensure_table(self):
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS ods_macro_indicator (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_date  TEXT,
                indicator_name  TEXT,
                indicator_value REAL,
                source          TEXT,
                update_time     TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_ods_macro_date_name
                ON ods_macro_indicator (indicator_date, indicator_name);
        """)
        conn.commit()
        conn.close()

    def _load_existing_keys(self):
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql(
                "SELECT indicator_date, indicator_name FROM ods_macro_indicator",
                conn
            )
            return set(zip(df["indicator_date"], df["indicator_name"]))
        except Exception:
            return set()
        finally:
            conn.close()

    def _already_exists(self, indicator_date, indicator_name):
        return (indicator_date, indicator_name) in self._existing

    # ================================================================ #
    # 1. PMI
    # ================================================================ #
    def load_pmi(self):
        df = ak.macro_china_pmi()
        if df is None or df.empty:
            return None
        rows = []
        for _, row in df.iterrows():
            date_str = str(row["月份"]).strip()
            # "" -> "2026-05-01"
            if "年" in date_str:
                date_str = date_str.replace("年", "-").replace("月份", "-01")
            val = float(row["制造业-指数"])
            rows.append((date_str, val))
        return rows

    # ================================================================ #
    # 2. M2 
    # ================================================================ #
    def load_m2(self):
        df = ak.macro_china_money_supply()
        if df is None or df.empty:
            return None
        col = [c for c in df.columns if "M2" in c and "同比" in c]
        if not col:
            return None
        rows = []
        for _, row in df.iterrows():
            date_str = str(row["月份"]).strip()
            if "年" in date_str:
                date_str = date_str.replace("年", "-").replace("月份", "-01")
            val = float(row[col[0]])
            rows.append((date_str, val))
        return rows

    # ================================================================ #
    # 3.  
    # ================================================================ #
    def load_yield_spread(self):
        df = ak.bond_zh_us_rate()
        if df is None or df.empty:
            return None
        cn_col = "中国国债收益率10年"
        us_col = "美国国债收益率10年"
        valid = df.dropna(subset=[cn_col, us_col])
        if valid.empty:
            return None
        rows = []
        for _, row in valid.iterrows():
            date_str = str(row["日期"]).split(" ")[0]
            # datetime.date -> str
            if hasattr(row["日期"], "strftime"):
                date_str = row["日期"].strftime("%Y-%m-%d")
            spread = round(float(row[cn_col]) - float(row[us_col]), 4)
            rows.append((date_str, spread))
        return rows

    # ================================================================ #
    # 4. CPI 
    # ================================================================ #
    def load_cpi(self):
        df = ak.macro_china_cpi_yearly()
        if df is None or df.empty:
            return None
        valid = df.dropna(subset=["今值"])
        if valid.empty:
            return None
        rows = []
        for _, row in valid.iterrows():
            date_str = str(row["日期"]).split(" ")[0]
            if hasattr(row["日期"], "strftime"):
                date_str = row["日期"].strftime("%Y-%m-%d")
            val = float(row["今值"])
            rows.append((date_str, val))
        return rows

    # ================================================================ #
    # 5. PPI 
    # ================================================================ #
    def load_ppi(self):
        df = ak.macro_china_ppi_yearly()
        if df is None or df.empty:
            return None
        valid = df.dropna(subset=["今值"])
        if valid.empty:
            return None
        rows = []
        for _, row in valid.iterrows():
            date_str = str(row["日期"]).split(" ")[0]
            if hasattr(row["日期"], "strftime"):
                date_str = row["日期"].strftime("%Y-%m-%d")
            val = float(row["今值"])
            rows.append((date_str, val))
        return rows

    # ================================================================ #
    # 6.  
    # ================================================================ #
    def load_fed_rate(self):
        df = ak.macro_bank_usa_interest_rate()
        if df is None or df.empty:
            return None
        valid = df.dropna(subset=["今值"])
        if valid.empty:
            return None
        rows = []
        for _, row in valid.iterrows():
            date_str = str(row["日期"]).split(" ")[0]
            if hasattr(row["日期"], "strftime"):
                date_str = row["日期"].strftime("%Y-%m-%d")
            val = float(row["今值"])
            rows.append((date_str, val))
        return rows

    # ================================================================ #
    # 7.  300 PE
    # ================================================================ #
    def load_csi300_pe(self):
        df = ak.stock_index_pe_lg()
        if df is None or df.empty:
            return None
        rows = []
        for _, row in df.iterrows():
            date_str = str(row["日期"]).split(" ")[0]
            if hasattr(row["日期"], "strftime"):
                date_str = row["日期"].strftime("%Y-%m-%d")
            val = float(row["滚动市盈率"])
            rows.append((date_str, val))
        return rows

    # ================================================================ #
    # 8.    ( 22  )
    # ================================================================ #
    def load_north_flow(self):
        df = ak.stock_hsgt_hist_em()
        if df is None or df.empty:
            return None
        col = "当日成交净买额"
        valid = df.dropna(subset=[col])
        if valid.empty:
            return None
        rows = []
        for _, row in valid.iterrows():
            date_str = str(row["日期"]).split(" ")[0]
            if hasattr(row["日期"], "strftime"):
                date_str = row["日期"].strftime("%Y-%m-%d")
            val = float(row[col])
            rows.append((date_str, val))
        return rows

    # ================================================================ #
    # fetch_all:  ->  ;  ->  
    # ================================================================ #
    def fetch_all(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        indicators = self.config["indicators"]
        total_new = 0
        total_skip = 0
        total_fail = 0
        all_new_rows = []

        for name, cfg in indicators.items():
            ak_func = cfg["ak_func"]
            loader_name = INDICATOR_LOADERS.get(ak_func)
            if not loader_name:
                print(f"  [{ak_func}] {name} = SKIP (no loader)")
                continue
            try:
                fn = getattr(self, loader_name)
                all_rows = fn()
                if all_rows is None or len(all_rows) == 0:
                    print(f"  [{ak_func}] {name} = FAILED (empty)")
                    total_fail += 1
                    continue
                # Filter: only keep rows that don't exist yet
                new_rows = [
                    (date_str, val)
                    for (date_str, val) in all_rows
                    if not self._already_exists(date_str, name)
                ]
                for (date_str, val) in new_rows:
                    all_new_rows.append((date_str, name, val, ak_func, now))
                skipped = len(all_rows) - len(new_rows)
                total_new += len(new_rows)
                total_skip += skipped
                print(f"  [{ak_func}] {name} = {len(all_rows)} total, {len(new_rows)} new, {skipped} skip")
            except Exception as e:
                print(f"  [WARN] [{ak_func}] {name} ERROR (existing ODS preserved): {e}")
                traceback.print_exc()
                total_fail += 1

        self.new_rows = all_new_rows
        print(f"\nSummary: {total_new} new + {total_skip} skip / {total_fail} fail / {len(indicators)} indicators")

    # ================================================================ #
    # save: only INSERT new rows, never DELETE
    # ================================================================ #
    def save_result(self):
        if not self.new_rows:
            print("  (no new rows to save)")
            return
        conn = sqlite3.connect(self.db_path)
        conn.executemany(
            "INSERT INTO ods_macro_indicator (indicator_date, indicator_name, indicator_value, source, update_time) VALUES (?, ?, ?, ?, ?)",
            self.new_rows
        )
        conn.commit()
        conn.close()
        print(f"Saved {len(self.new_rows)} new rows to ods_macro_indicator")

    def run(self):
        print("=" * 80)
        print("Macro Loader: fetching 8 indicators from AKShare...")
        print("=" * 80)
        self.fetch_all()
        self.save_result()
        print("[OK] MacroLoader completed")


if __name__ == "__main__":
    MacroLoader().run()
