# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pandas as pd

from datetime import datetime

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
)

from engine.base_engine import BaseEngine


class MacroIndicatorEngine(BaseEngine):

    def __init__(self):
        super().__init__()

    def extract(self):
        """Extract: V1先使用固定宏观数据"""

        self.macro_data = [
            {
                "indicator_name": "PMI",
                "indicator_value": 50.4,
                "trend": "上升"
            },
            {
                "indicator_name": "社会融资增速",
                "indicator_value": 8.7,
                "trend": "上升"
            },
            {
                "indicator_name": "美联储利率",
                "indicator_value": 4.25,
                "trend": "下降"
            },
            {
                "indicator_name": "美国10年国债收益率",
                "indicator_value": 4.38,
                "trend": "下降"
            },
            {
                "indicator_name": "美元指数DXY",
                "indicator_value": 98.60,
                "trend": "下降"
            }
        ]

    def transform(self):
        """Transform: 计算宏观评分"""

        rows = []

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in self.macro_data:

            name = item["indicator_name"]
            value = item["indicator_value"]
            trend = item["trend"]

            score = 50
            comment = ""

            # PMI
            if name == "PMI":

                if value >= 50:
                    score = 80
                    comment = "经济处于扩张区间"

                else:
                    score = 40
                    comment = "经济处于收缩区间"

            # 社融
            elif name == "社会融资增速":

                if trend == "上升":
                    score = 80
                    comment = "流动性改善"

                else:
                    score = 50
                    comment = "流动性偏弱"

            # 美联储利率
            elif name == "美联储利率":

                if trend == "下降":
                    score = 90
                    comment = "进入降息周期"

                else:
                    score = 40
                    comment = "加息周期"

            # 美债收益率
            elif name == "美国10年国债收益率":

                if value < 4.0:
                    score = 85
                    comment = "利好成长股"

                elif value < 4.5:
                    score = 70
                    comment = "中性"

                else:
                    score = 40
                    comment = "压制成长股估值"

            # DXY
            elif name == "美元指数DXY":

                if value < 100:
                    score = 80
                    comment = "利好全球风险资产"

                elif value < 105:
                    score = 60
                    comment = "中性"

                else:
                    score = 40
                    comment = "压制风险资产"

            rows.append(
                [
                    name,
                    value,
                    trend,
                    score,
                    comment,
                    now
                ]
            )

        self.result_df = pd.DataFrame(
            rows,
            columns=[
                "indicator_name",
                "indicator_value",
                "trend",
                "score",
                "comment",
                "update_time"
            ]
        )

    def load(self):
        """Load"""

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            """
            DELETE FROM dwd_macro_indicator
            """
        )

        self.result_df.to_sql(
            "dwd_macro_indicator",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()
        conn.close()

    def print_result(self):

        print()
        print("=" * 100)
        print("宏观指标")
        print("=" * 100)

        print(
            self.result_df[
                [
                    "indicator_name",
                    "indicator_value",
                    "trend",
                    "score"
                ]
            ]
        )

    def run(self):

        super().run()
        self.print_result()


if __name__ == "__main__":

    MacroIndicatorEngine().run()