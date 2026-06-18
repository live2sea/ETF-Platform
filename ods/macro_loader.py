import sqlite3
import json
import os
import pandas as pd
import akshare as ak
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "macro_weights.json")
DB_PATH = os.path.join(ROOT, "data", "etf.db")

INDICATOR_LOADERS = {
    "macro_china_pmi":                  "load_pmi",
    "macro_china_money_supply":         "load_m2",
    "macro_china_china_us_yield_spread":"load_yield_spread",
    "macro_china_cpi_yearly":           "load_cpi",
    "macro_china_ppi_yearly":           "load_ppi",
    "macro_usa_interest_rate":          "load_fed_rate",
    "stock_a_pe_csi300":                "load_csi300_pe",
    "stock_hsgt_north_net_flow_in_em":  "load_north_flow",
}


class MacroLoader:

    def __init__(self):
        self.db_path = DB_PATH
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def load_pmi(self):
        df = ak.macro_china_pmi()
        if df is None or df.empty:
            return None
        col_date = [c for c in df.columns if "\u65e5\u671f" in c or "date" in c.lower()]
        col_val  = [c for c in df.columns if "\u5236\u9020\u4e1a" in c or "PMI" in c.upper()]
        if not col_date or not col_val:
            return None
        return float(df.iloc[-1][col_val[0]])

    def load_m2(self):
        try:
            df = ak.macro_china_money_supply()
            if df is None or df.empty:
                return None
            col_m2 = [c for c in df.columns if "M2" in c.upper() and "\u540c\u6bd4" in c]
            if not col_m2:
                col_m2 = [c for c in df.columns if "M2" in c.upper()]
            if not col_m2:
                return None
            return float(df.iloc[-1][col_m2[0]])
        except Exception:
            return None

    def load_yield_spread(self):
        try:
            cn = ak.bond_china_yield(start_date="20200101")
            us = ak.bond_usa_yield(start_date="20200101", end_date=datetime.now().strftime("%Y%m%d"))
            if cn is None or cn.empty or us is None or us.empty:
                return None
            cn_10y = float(cn.iloc[-1]["10\u5e74\u671f"])
            us_10y = float(us.iloc[-1]["10\u5e74\u671f"])
            return round(cn_10y - us_10y, 4)
        except Exception:
            return None

    def load_cpi(self):
        try:
            df = ak.macro_china_cpi_yearly()
            if df is None or df.empty:
                return None
            col = [c for c in df.columns if "\u540c\u6bd4" in c or "CPI" in c.upper()]
            if not col:
                return None
            return float(df.iloc[-1][col[0]])
        except Exception:
            return None

    def load_ppi(self):
        try:
            df = ak.macro_china_ppi_yearly()
            if df is None or df.empty:
                return None
            col = [c for c in df.columns if "\u540c\u6bd4" in c or "PPI" in c.upper()]
            if not col:
                return None
            return float(df.iloc[-1][col[0]])
        except Exception:
            return None

    def load_fed_rate(self):
        try:
            df = ak.macro_usa_interest_rate()
            if df is None or df.empty:
                return None
            col = [c for c in df.columns if "\u5229\u7387" in c or "rate" in c.lower()]
            if not col:
                return None
            return float(df.iloc[-1][col[0]])
        except Exception:
            return None

    def load_csi300_pe(self):
        try:
            df = ak.stock_a_pe(symbol="\u6caa\u6df1300")
            if df is None or df.empty:
                df = ak.stock_a_pe_lg(symbol="\u6caa\u6df1300")
            if df is None or df.empty:
                return None
            col = [c for c in df.columns if "PE" in c.upper() or "\u5e02\u76c8\u7387" in c]
            if not col:
                return None
            return float(df.iloc[-1][col[0]])
        except Exception:
            return None

    def load_north_flow(self):
        try:
            df = ak.stock_hsgt_north_net_flow_in_em(symbol="\u5317\u5411")
            if df is None or df.empty:
                return None
            col = [c for c in df.columns if "\u51c0\u4e70\u5165" in c or "\u51c0\u6d41\u5165" in c]
            if not col:
                return None
            recent = df.head(22)
            total = recent[col[0]].sum()
            return float(total)
        except Exception:
            return None

    def fetch_all(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        indicator_date = datetime.now().strftime("%Y-%m-%d")
        rows = []
        indicators = self.config["indicators"]
        for name, cfg in indicators.items():
            ak_func = cfg["ak_func"]
            loader_name = INDICATOR_LOADERS.get(ak_func)
            value = None
            if loader_name:
                try:
                    fn = getattr(self, loader_name)
                    value = fn()
                except Exception:
                    value = None
            if value is not None:
                rows.append([indicator_date, name, value, ak_func, now])
                print(f"  [{ak_func}] {name} = {value}")
            else:
                print(f"  [{ak_func}] {name} = FAILED")
        self.data = rows
        print(f"Fetched {len(rows)}/{len(indicators)} indicators")

    def save_result(self):
        conn = sqlite3.connect(self.db_path)
        for row in self.data:
            conn.execute(
                "INSERT OR REPLACE INTO ods_macro_indicator (indicator_date, indicator_name, indicator_value, source, update_time) VALUES (?, ?, ?, ?, ?)",
                row
            )
        conn.commit()
        conn.close()
        print(f"Saved {len(self.data)} rows to ods_macro_indicator")

    def run(self):
        print("=" * 80)
        print("Macro Loader: fetching 8 indicators from AKShare...")
        print("=" * 80)
        self.fetch_all()
        self.save_result()
        print("[OK] MacroLoader completed")


if __name__ == "__main__":
    MacroLoader().run()
