# -*- coding: utf-8 -*-
"""Test: ETF score macro integration — verify category bonus per phase"""
import os, sys, json, unittest, sqlite3, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.strategy.etf_score_engine_v2 import ETFScoreEngineV2

class TestETFScoreMacro(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_es_ut.db"
        self.engine = ETFScoreEngineV2()
        self.engine.db_path = self.db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("DROP TABLE IF EXISTS dwd_allocation"); conn.execute("CREATE TABLE dwd_allocation (etf_code TEXT, etf_name TEXT, allocation_pct REAL)")
        conn.execute("DROP TABLE IF EXISTS dwd_floating_profit"); conn.execute("CREATE TABLE dwd_floating_profit (etf_code TEXT, floating_profit REAL, floating_profit_pct REAL)")
        conn.execute("DROP TABLE IF EXISTS dwd_profit_analysis"); conn.execute("CREATE TABLE dwd_profit_analysis (etf_code TEXT, realized_profit REAL)")
        conn.execute("DROP TABLE IF EXISTS dwd_macro_environment"); conn.execute("CREATE TABLE dwd_macro_environment (eval_date TEXT PRIMARY KEY, effective_phase TEXT, position_cap INTEGER)")
        conn.execute("DROP TABLE IF EXISTS dwd_etf_score_v2"); conn.execute("CREATE TABLE dwd_etf_score_v2 (etf_code TEXT PRIMARY KEY, etf_name TEXT, category_name TEXT, allocation_pct REAL, floating_profit REAL, floating_profit_pct REAL, realized_profit REAL, macro_bonus INTEGER, total_score INTEGER, score_level TEXT, suggestion TEXT, update_time TEXT)")
        conn.execute("INSERT INTO dwd_allocation VALUES ('510880','红利ETF',8)")
        conn.execute("INSERT INTO dwd_floating_profit VALUES ('510880',100,5)")
        conn.execute("INSERT INTO dwd_profit_analysis VALUES ('510880',3000)")
        conn.execute("INSERT INTO dwd_macro_environment VALUES ('2026-06-18','防御',40)")
        conn.commit()
        conn.close()

    def test_defense_phase_bonus_red(self):
        self.engine.extract()
        self.engine.transform()
        row = self.engine.result_df[self.engine.result_df["etf_code"]=="510880"].iloc[0]
        self.assertEqual(int(row["macro_bonus"]), 20)

    def test_total_score_includes_macro(self):
        self.engine.extract()
        self.engine.transform()
        row = self.engine.result_df.iloc[0]
        self.assertIn("macro_bonus", self.engine.result_df.columns)
        self.assertGreaterEqual(int(row["total_score"]), int(row["macro_bonus"]))

    def test_unknown_category_default_bonus(self):
        self.engine.macro_env = pd.DataFrame([{"effective_phase": "扩张"}])
        bonus = self.engine._get_macro_bonus("999999")
        self.assertEqual(bonus, 10)

if __name__ == "__main__":
    unittest.main()
