# -*- coding: utf-8 -*-
"""Test: end-to-end macro integration — simulate 3 macro days"""
import os, sys, json, unittest, sqlite3, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.macro.macro_indicator_engine import MacroIndicatorEngine
from engine.macro.macro_environment_engine import MacroEnvironmentEngine

class TestMacroIntegration(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_macro_int.db"
        # Setup tables
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE ods_macro_indicator (indicator_date TEXT, indicator_name TEXT, indicator_value REAL);
            CREATE TABLE dwd_macro_indicator (indicator_date TEXT, indicator_name TEXT, indicator_value REAL, score INTEGER, trend TEXT, comment TEXT, update_time TEXT, PRIMARY KEY (indicator_date, indicator_name));
            CREATE TABLE dwd_macro_environment (eval_date TEXT PRIMARY KEY, macro_score REAL, macro_phase TEXT, trend_score REAL, acceleration TEXT, effective_phase TEXT, position_cap INTEGER, update_time TEXT);
        """)
        # Insert 3 days of ODS data
        indicators_config = {
            "PMI": 52, "M2同比": 11, "中美利差": -1, "CPI年率": 2,
            "PPI年率": 1, "美联储利率": 4.5, "沪深300 PE": 14, "北向月度净流入": 300
        }
        for day in ["2026-06-16", "2026-06-17", "2026-06-18"]:
            for name, val in indicators_config.items():
                conn.execute("INSERT INTO ods_macro_indicator VALUES (?,?,?)", (day, name, val))
        conn.commit()
        conn.close()

    def test_three_day_pipeline(self):
        ind_engine = MacroIndicatorEngine()
        ind_engine.db_path = self.db_path
        ind_engine.extract()
        ind_engine.transform()
        ind_engine.load()

        env_engine = MacroEnvironmentEngine()
        env_engine.db_path = self.db_path
        env_engine.extract()
        env_engine.transform()
        env_engine.load()

        conn = sqlite3.connect(self.db_path)
        env = pd.read_sql("SELECT * FROM dwd_macro_environment", conn)
        conn.close()
        self.assertFalse(env.empty)
        self.assertIn("macro_score", env.columns)
        self.assertIn("effective_phase", env.columns)
        self.assertIn("position_cap", env.columns)
        print(f"PASS: macro_score={env.iloc[0]['macro_score']}, phase={env.iloc[0]['effective_phase']}, cap={env.iloc[0]['position_cap']}")

if __name__ == "__main__":
    unittest.main()
