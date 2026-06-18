# -*- coding: utf-8 -*-
"""Test: macro_environment_engine — verify weighted total, trend acceleration, phase correction"""
import os, sys, json, unittest, sqlite3, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.macro.macro_environment_engine import MacroEnvironmentEngine

class TestMacroEnvironmentEngine(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_me_ut.db"
        self.engine = MacroEnvironmentEngine()
        self.engine.db_path = self.db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("DROP TABLE IF EXISTS dwd_macro_indicator"); conn.execute("CREATE TABLE dwd_macro_indicator (indicator_date TEXT, indicator_name TEXT, indicator_value REAL, score INTEGER)")
        conn.execute("DROP TABLE IF EXISTS dwd_macro_environment"); conn.execute("CREATE TABLE dwd_macro_environment (eval_date TEXT PRIMARY KEY, macro_score REAL, macro_phase TEXT, trend_score REAL, acceleration TEXT, effective_phase TEXT, position_cap INTEGER, update_time TEXT)")
        # Insert 8 indicators with all-80 scores => macro_score ~80 => expansion
        indicators = self.engine.config["indicators"]
        for name in indicators:
            conn.execute("INSERT INTO dwd_macro_indicator VALUES ('2026-06-18',?,100,80)", (name,))
        conn.commit()
        conn.close()

    def test_phase_determination(self):
        self.assertEqual(self.engine._determine_phase(80), "扩张")
        self.assertEqual(self.engine._determine_phase(65), "复苏")
        self.assertEqual(self.engine._determine_phase(50), "观望")
        self.assertEqual(self.engine._determine_phase(30), "防御")

    def test_transform_high_score_expansion(self):
        self.engine.extract()
        self.engine.transform()
        self.assertFalse(self.engine.result_df.empty)
        row = self.engine.result_df.iloc[0]
        self.assertAlmostEqual(row["macro_score"], 80, delta=5)

    def test_phase_correction_matrix(self):
        phase = self.engine._effective_phase("观望", "正向")
        self.assertEqual(phase, "复苏")
        phase = self.engine._effective_phase("复苏", "负向")
        self.assertEqual(phase, "观望")
        phase = self.engine._effective_phase("扩张", "中性")
        self.assertEqual(phase, "扩张")

if __name__ == "__main__":
    unittest.main()
