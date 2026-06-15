# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class PositionHealthEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: 加载仓位与分类数据"""
        conn = sqlite3.connect(self.db_path)
        self.allocation_df = pd.read_sql("select * from dwd_allocation", conn)
        self.category_df = pd.read_sql("select * from dwd_category_allocation", conn)
        conn.close()

    def transform(self):
        """Transform: 执行四项健康检查"""
        result = [
            self._check_single_etf(),
            self._check_category(),
            self._check_etf_count(),
            self._check_overlap(),
        ]
        self.result_df = pd.DataFrame(result)
        self.result_df["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _check_single_etf(self):
        max_row = self.allocation_df.loc[self.allocation_df["allocation_pct"].idxmax()]
        pct = float(max_row["allocation_pct"])
        if pct > 30:
            level, suggestion = "危险", "立即降低单只ETF仓位"
        elif pct > 20:
            level, suggestion = "偏高", "暂停加仓"
        else:
            level, suggestion = "正常", "继续持有"
        return {"health_item": "最大单ETF仓位", "item_value": pct, "risk_level": level, "suggestion": suggestion}

    def _check_category(self):
        max_row = self.category_df.loc[self.category_df["allocation_pct"].idxmax()]
        pct = float(max_row["allocation_pct"])
        name = max_row["category_name"]
        if pct > 40:
            level, suggestion = "危险", f"{name}仓位过高"
        elif pct > 25:
            level, suggestion = "注意", f"{name}仓位偏高"
        else:
            level, suggestion = "正常", "配置合理"
        return {"health_item": f"主题集中度({name})", "item_value": pct, "risk_level": level, "suggestion": suggestion}

    def _check_etf_count(self):
        count = len(self.allocation_df)
        if count > 20:
            level, suggestion = "危险", "ETF数量过多"
        elif count > 15:
            level, suggestion = "注意", "持仓略分散"
        else:
            level, suggestion = "正常", "持仓数量合理"
        return {"health_item": "ETF数量", "item_value": count, "risk_level": level, "suggestion": suggestion}

    def _check_overlap(self):
        nasdaq_group = ["159632", "159696", "159659", "513110", "513300"]
        overlap = self.allocation_df[self.allocation_df["etf_code"].isin(nasdaq_group)]
        count = len(overlap)
        if count >= 4:
            level, suggestion = "危险", "纳指ETF重复严重"
        elif count >= 3:
            level, suggestion = "注意", "存在重复持仓"
        else:
            level, suggestion = "正常", "无明显重叠"
        return {"health_item": "纳指ETF重叠", "item_value": count, "risk_level": level, "suggestion": suggestion}

    def load(self):
        """Load: 写入 dwd_position_health"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS dwd_position_health (health_item TEXT PRIMARY KEY, item_value REAL, risk_level TEXT, suggestion TEXT, update_time TEXT)")
        conn.execute("DELETE FROM dwd_position_health")
        self.result_df.to_sql("dwd_position_health", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        print()
        print("=" * 100)
        print("组合健康度分析")
        print("=" * 100)
        print(self.result_df[["health_item", "item_value", "risk_level", "suggestion"]])

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    PositionHealthEngine().run()
