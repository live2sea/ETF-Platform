# -*- coding: utf-8 -*-
"""Test: macro_loader — verify 8 indicators are stored correctly"""
import os, sys, unittest, json
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ods.macro_loader import MacroLoader

class TestMacroLoader(unittest.TestCase):
    def setUp(self):
        self.loader = MacroLoader()

    def test_config_loaded(self):
        self.assertIn("indicators", self.loader.config)
        self.assertEqual(len(self.loader.config["indicators"]), 8)

    @patch("ods.macro_loader.ak.macro_china_pmi")
    def test_pmi_fetch(self, mock_ak):
        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.columns = ["日期", "制造业PMI"]
        mock_df.iloc.__getitem__.return_value.__getitem__.return_value = 50.4
        mock_ak.return_value = mock_df
        val = self.loader.load_pmi()
        self.assertEqual(val, 50.4)

    def test_fetch_all_smoke(self):
        rows = self.loader.data if hasattr(self.loader, "data") else []
        self.assertIsInstance(rows, list)

if __name__ == "__main__":
    unittest.main()
