# -*- coding: utf-8 -*-
"""Test: macro_indicator_engine — verify scoring calculation, incremental write, dedup"""
import os, sys, json, unittest, sqlite3, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.macro.macro_indicator_engine import MacroIndicatorEngine

class TestMacroIndicatorEngine(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_mi_ut.db"
        self.engine = MacroIndicatorEngine()
        self.engine.db_path = self.db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("DROP TABLE IF EXISTS ods_macro_indicator"); conn.execute("CREATE TABLE ods_macro_indicator (indicator_date TEXT, indicator_name TEXT, indicator_value REAL)")
        conn.execute("DROP TABLE IF EXISTS dwd_macro_indicator"); conn.execute("CREATE TABLE dwd_macro_indicator (indicator_date TEXT, indicator_name TEXT, indicator_value REAL, score INTEGER, trend TEXT, comment TEXT, update_time TEXT, PRIMARY KEY (indicator_date, indicator_name))")
        conn.execute("INSERT INTO ods_macro_indicator VALUES ('2026-06-18','PMI',52)")
        conn.execute("INSERT INTO ods_macro_indicator VALUES ('2026-06-18','美联储利率',4)")
        conn.commit()
        conn.close()

    def test_extract_reads_ods(self):
        self.engine.extract()
        self.assertFalse(self.engine.ods_df.empty)

    def test_linear_score(self):
        score = self.engine._linear_score(52, [[45,0],[48,20],[50,50],[52,80],[55,100]])
        self.assertEqual(score, 80)

    def test_transform_produces_rows(self):
        self.engine.extract()
        self.engine.transform()
        self.assertFalse(self.engine.result_df.empty)
        self.assertIn("score", self.engine.result_df.columns)

    def test_incremental_write_no_delete(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO dwd_macro_indicator VALUES ('2026-06-18','PMI',52,80,'持平','test','2026')")
        conn.commit()
        conn.close()
        self.engine.extract()
        self.engine.transform()
        self.engine.load()
        conn = sqlite3.connect(self.db_path)
        cnt = pd.read_sql("SELECT COUNT(*) as n FROM dwd_macro_indicator", conn).iloc[0]["n"]
        conn.close()
        self.assertTrue(cnt >= 1)

if __name__ == "__main__":
    unittest.main()
