#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 trade_watcher 批量导入 + 去重逻辑。"""

import os
import sys
import tempfile
import shutil
import unittest
import glob

import pandas as pd
import openpyxl

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ods.trade_import import TradeImporter
from tools.trade_watcher import run as run_trade_watcher


class TestTradeWatcher(unittest.TestCase):
    """验证批量导入和去重逻辑."""

    def setUp(self):
        """准备临时目录和数据库."""
        self.tmpdir = tempfile.mkdtemp()
        # watcher 使用 ROOT/data/import/ 路径，所以在这里构造
        self.data_dir = os.path.join(self.tmpdir, "data")
        self.import_dir = os.path.join(self.data_dir, "import")
        self.archive_dir = os.path.join(self.import_dir, "archive")
        self.db_path = os.path.join(self.tmpdir, "etf.db")
        os.makedirs(self.archive_dir, exist_ok=True)

        # 初始化 SQLite 表
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ods_trade_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_date TEXT,
                trade_time TEXT,
                etf_code TEXT,
                etf_name TEXT,
                trade_type TEXT,
                quantity INTEGER,
                price REAL,
                amount REAL,
                fee REAL,
                tax REAL,
                settlement_amount REAL
            )
        """)
        conn.commit()
        conn.close()

        # 临时替换 TradeImporter.db_path 和系统路径
        self._orig_db_path = TradeImporter.__init__

    def tearDown(self):
        """清理临时目录."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_excel(self, fname, records):
        """构造测试用 Excel 文件。"""
        fp = os.path.join(self.import_dir, fname)
        df = pd.DataFrame(records)
        df.to_excel(fp, index=False)
        return fp

    def _count_records(self, importer):
        """统计 ods_trade_record 记录数."""
        import sqlite3
        conn = sqlite3.connect(importer.db_path)
        cur = conn.execute("SELECT COUNT(*) FROM ods_trade_record")
        count = cur.fetchone()[0]
        conn.close()
        return count

    def _make_base_records(self, n, suffix=""):
        """生成 n 条基础记录."""
        return [
            {
                "成交日期": f"2026-06-{10+i:02d}",
                "成交时间": "10:00:00",
                "证券代码": f"51005{i}",
                "证券名称": f"ETF_{i}{suffix}",
                "买卖标志": "买入",
                "成交数量": 100 * (i + 1),
                "成交价格": 1.0 + i * 0.1,
                "成交金额": 100 * (i + 1) * (1.0 + i * 0.1),
                "手续费": 5.0,
                "印花税": 0,
                "清算金额": 100 * (i + 1) * (1.0 + i * 0.1) - 5.0,
            }
            for i in range(n)
        ]

    def test_first_import_writes_all_new(self):
        """第一次导入：3 条全新记录 → 全部写入."""
        records = self._make_base_records(3)
        fp = self._make_excel("trade_01.xlsx", records)

        importer = TradeImporter()
        importer.db_path = self.db_path
        importer.run(fp)

        self.assertEqual(self._count_records(importer), 3)

    def test_re_import_same_file_skips_all(self):
        """第二次导入同一文件 → 0 条写入."""
        records = self._make_base_records(3)
        fp = self._make_excel("trade_01.xlsx", records)

        importer = TradeImporter()
        importer.db_path = self.db_path

        # 第一次导入
        importer.run(fp)
        self.assertEqual(self._count_records(importer), 3)

        # 第二次导入同一文件
        importer.run(fp)
        self.assertEqual(self._count_records(importer), 3, "重复导入不应增加记录")

    def test_incremental_import(self):
        """增量导入：已有 3 条，再导入含 2 新 + 1 旧的 Excel → 只新增 2 条."""
        # 第一批：3 条
        importer = TradeImporter()
        importer.db_path = self.db_path

        records_a = self._make_base_records(3)
        fp_a = self._make_excel("trade_a.xlsx", records_a)
        importer.run(fp_a)
        self.assertEqual(self._count_records(importer), 3)

        # 第二批：2 新 + 1 旧（新记录用不同日期避免撞 key）
        records_b = [
            {
                "成交日期": "2026-07-01",
                "成交时间": "10:00:00",
                "证券代码": "510070",
                "证券名称": "ETF_new_A",
                "买卖标志": "买入",
                "成交数量": 700,
                "成交价格": 1.77,
                "成交金额": 1239.0,
                "手续费": 5.0,
                "印花税": 0,
                "清算金额": 1234.0,
            },
            {
                "成交日期": "2026-07-02",
                "成交时间": "10:00:00",
                "证券代码": "510071",
                "证券名称": "ETF_new_B",
                "买卖标志": "卖出",
                "成交数量": 800,
                "成交价格": 2.88,
                "成交金额": 2304.0,
                "手续费": 5.0,
                "印花税": 0,
                "清算金额": 2299.0,
            },
        ]
        records_b.append(records_a[0])  # 重复记录
        fp_b = self._make_excel("trade_b.xlsx", records_b)
        importer.run(fp_b)

        self.assertEqual(self._count_records(importer), 5)

    def test_trade_watcher_scans_and_archives(self):
        """trade_watcher 批量扫描：成功后归档."""
        records = self._make_base_records(3)
        fp = self._make_excel("trade_01.xlsx", records)

        import tools.trade_watcher as tw

        importer = TradeImporter()
        importer.db_path = self.db_path

        # Patch watcher 的 ROOT 和 importer
        _orig_root = tw.ROOT
        _orig_TradeImporter = tw.TradeImporter
        tw.ROOT = self.tmpdir
        tw.TradeImporter = lambda: importer

        try:
            tw.run()

            # 验证文件已归档（源文件应不在 import 目录下）
            src_files = glob.glob(os.path.join(self.import_dir, "*.xlsx"))
            self.assertEqual(
                len(src_files), 0,
                "导入成功后应归档"
            )

            # 验证归档目录有文件
            arc_files = glob.glob(os.path.join(self.archive_dir, "*.xlsx"))
            self.assertEqual(
                len(arc_files), 1,
                "归档目录应有 1 个文件"
            )
        finally:
            tw.ROOT = _orig_root
            tw.TradeImporter = _orig_TradeImporter


if __name__ == "__main__":
    unittest.main()
