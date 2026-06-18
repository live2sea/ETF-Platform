#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量扫描 data/import/*.xlsx，调用 TradeImporter 导入并归档。"""

import os
import sys
import shutil
import glob

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ods.trade_import import TradeImporter


def run():
    import_dir = os.path.join(ROOT, "data", "import")
    archive_dir = os.path.join(import_dir, "archive")

    # 确保目录存在
    os.makedirs(archive_dir, exist_ok=True)

    # 扫描 Excel 文件
    files = glob.glob(os.path.join(import_dir, "*.xlsx"))
    if not files:
        print("[trade_watcher] 没有待导入的文件")
        return

    print(f"[trade_watcher] 发现 {len(files)} 个待导入文件")

    success_count = 0
    fail_count = 0

    for fp in files:
        fname = os.path.basename(fp)
        print(f"[trade_watcher] 正在导入: {fname}")
        try:
            importer = TradeImporter()
            importer.run(fp)

            # 导入成功 → 移动到 archive
            dest = os.path.join(archive_dir, fname)
            shutil.move(fp, dest)
            print(f"[trade_watcher] 已归档: {fname}")
            success_count += 1

        except Exception as e:
            print(f"[trade_watcher] 导入失败: {fname}")
            print(f"  错误: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

    print(f"[trade_watcher] 完成: 成功 {success_count}, 失败 {fail_count}")


if __name__ == "__main__":
    run()
