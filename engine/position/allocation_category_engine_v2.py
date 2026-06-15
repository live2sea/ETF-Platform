#!/usr/bin/env python3
# 解释：该脚本定义了一个AllocationCategoryEngine类，用于计算ETF的分类仓位结构。
# 它从SQLite数据库中加载仓位分配数据，按分类汇总市值，计算各分类的占比和风险等级，并将结果保存到数据库中。
# 最后，在主程序中创建一个AllocationCategoryEngine实例，执行计算并打印分析结果。

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.base_engine import BaseEngine


class AllocationCategoryEngine(BaseEngine):

    def __init__(self):
        super().__init__()

        # ETF 分类映射
        # 后续可以迁移数据库配置表
        self.category_map = {
            "159740": "港股科技",
            "513580": "港股科技",
            "513980": "港股科技",
            "159632": "美股科技",
            "159696": "美股科技",
            "513300": "美股科技",
            "513110": "美股科技",
            "159659": "美股科技",
            "513400": "美股宽基",
            "510880": "红利",
            "563020": "红利",
            "513000": "日本",
            "513800": "日本",
            "159561": "欧洲",
            "164824": "印度",
            "512170": "医疗",
            "159865": "农业",
            "159529": "消费",
        }

    def extract(self):
        """Extract: 加载仓位分配数据"""
        conn = sqlite3.connect(self.db_path)

        self.allocation_df = pd.read_sql(
            """
            select etf_code, etf_name, market_value
            from dwd_allocation
            """,
            conn,
        )

        conn.close()

        self.allocation_df["etf_code"] = (
            self.allocation_df["etf_code"]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.strip()
            .str.zfill(6)
        )
        self.allocation_df["market_value"] = pd.to_numeric(
            self.allocation_df["market_value"], errors="coerce"
        )

    def get_risk_level(self, pct):
        """根据占比返回风险等级"""
        if pct >= 35:
            return "高风险"
        elif pct >= 20:
            return "中风险"
        else:
            return "低风险"

    def transform(self):
        """Transform: 按分类汇总，计算占比与风险等级"""
        df = self.allocation_df

        df = df.copy()

        if len(df) == 0:
            print("dwd_allocation为空")
            self.result_df = pd.DataFrame()
            return

        df = df.dropna(subset=["market_value"])
        total_market_value = df["market_value"].sum()

        if total_market_value <= 0:
            print("总市值异常，请检查 dwd_allocation")
            self.result_df = pd.DataFrame()
            return

        # 分类
        df["category_name"] = df["etf_code"].map(self.category_map)

        # 未配置 ETF
        unknown = df[df["category_name"].isna()]
        if len(unknown) > 0:
            print()
            print("=" * 80)
            print("发现未分类ETF")
            print("=" * 80)
            print(unknown[["etf_code", "etf_name"]])
            print()
            df["category_name"] = df["category_name"].fillna("其它")

        # 聚合
        result = (
            df.groupby("category_name", as_index=False)
            .agg(
                market_value=("market_value", "sum"),
                etf_count=("etf_code", "count"),
            )
        )

        result["allocation_pct"] = (
            result["market_value"] / total_market_value * 100
        ).round(2)

        result["risk_level"] = result["allocation_pct"].apply(self.get_risk_level)
        result["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = result.sort_values("allocation_pct", ascending=False)

        self.result_df = result

    def load(self):
        """Load: 写入 dwd_category_allocation"""
        if len(self.result_df) == 0:
            return

        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dwd_category_allocation")
        self.result_df.to_sql("dwd_category_allocation", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def print_result(self):
        """打印分类仓位分析报告"""
        if len(self.result_df) == 0:
            return

        total_market_value = self.result_df["market_value"].sum()

        print()
        print("=" * 90)
        print("国家 / 主题仓位分析")
        print("=" * 90)
        print()
        print(f"总市值：{total_market_value:,.2f}")
        print()

        for _, row in self.result_df.iterrows():
            print(
                f"{row['category_name']:<10}"
                f"市值:{row['market_value']:>12.2f}"
                f" 占比:{row['allocation_pct']:>6.2f}%"
                f" ETF数:{row['etf_count']:>2}"
                f" 风险:{row['risk_level']}"
            )

    def run(self):
        super().run()
        self.print_result()


if __name__ == "__main__":
    AllocationCategoryEngine().run()
