import sqlite3
import pandas as pd

from datetime import datetime


class ETFScoreEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    # =====================================
    # 数据读取
    # =====================================

    def load_data(self):

        conn = sqlite3.connect(
            self.db_path
        )

        allocation = pd.read_sql("""

        select
            etf_code,
            etf_name,
            allocation_pct

        from dwd_allocation

        """, conn)

        floating = pd.read_sql("""

        select
            etf_code,
            floating_profit,
            floating_profit_pct

        from dwd_floating_profit

        """, conn)

        profit = pd.read_sql("""

        select
            etf_code,
            realized_profit

        from dwd_profit_analysis

        """, conn)

        conn.close()

        return (
            allocation,
            floating,
            profit
        )

    # =====================================
    # ETF分类
    # =====================================

    def get_category(self, code):

        mapping = {

            "159740":"港股科技",
            "513580":"港股科技",
            "513980":"港股科技",

            "159632":"美股科技",
            "159696":"美股科技",
            "513300":"美股科技",
            "513110":"美股科技",
            "159659":"美股科技",

            "513400":"美股宽基",

            "510880":"红利",
            "563020":"红利",

            "164824":"印度",

            "513000":"日本",
            "513800":"日本",

            "159865":"农业",

            "512170":"医疗",

            "159529":"消费",

            "159561":"欧洲"

        }

        return mapping.get(
            code,
            "其它"
        )

    # =====================================
    # 风险等级
    # =====================================

    def get_risk_level(self, category):

        high_risk = [

            "港股科技"

        ]

        medium_risk = [

            "美股科技"
        ]

        if category in high_risk:

            return "高风险"

        elif category in medium_risk:

            return "中风险"

        return "低风险"

    # =====================================
    # 评分规则
    # =====================================

    def profit_score(self, pct):

        if pct >= 15:
            return 30

        elif pct >= 10:
            return 25

        elif pct >= 0:
            return 20

        elif pct >= -10:
            return 12

        elif pct >= -20:
            return 6

        return 0

    def position_score(self, pct):

        if pct <= 5:
            return 25

        elif pct <= 10:
            return 20

        elif pct <= 15:
            return 15

        elif pct <= 20:
            return 8

        return 0

    def category_score(self, risk):

        mapping = {

            "高风险":0,
            "中风险":10,
            "低风险":25
        }

        return mapping.get(
            risk,
            0
        )

    def trade_score(
        self,
        realized_profit
    ):

        if realized_profit >= 5000:
            return 20

        elif realized_profit >= 2000:
            return 15

        elif realized_profit > 0:
            return 10

        return 5

    # =====================================
    # 建议
    # =====================================

    def get_suggestion(
        self,
        score
    ):

        if score >= 80:

            return "继续持有"

        elif score >= 60:

            return "谨慎持有"

        elif score >= 40:

            return "停止加仓"

        else:

            return "重点关注"

    # =====================================
    # 计算评分
    # =====================================

    def build_score(self):

        allocation,\
        floating,\
        profit = self.load_data()

        df = allocation.merge(
            floating,
            on="etf_code",
            how="left"
        )

        df = df.merge(
            profit,
            on="etf_code",
            how="left"
        )

        df.fillna(
            0,
            inplace=True
        )

        result = []

        for _, row in df.iterrows():

            category = self.get_category(
                row["etf_code"]
            )

            risk = self.get_risk_level(
                category
            )

            total_score = (

                self.profit_score(
                    row[
                        "floating_profit_pct"
                    ]
                )

                +

                self.position_score(
                    row[
                        "allocation_pct"
                    ]
                )

                +

                self.category_score(
                    risk
                )

                +

                self.trade_score(
                    row[
                        "realized_profit"
                    ]
                )

            )

            result.append({

                "etf_code":
                row["etf_code"],

                "etf_name":
                row["etf_name"],

                "category_name":
                category,

                "allocation_pct":
                row["allocation_pct"],

                "floating_profit":
                row[
                    "floating_profit"
                ],

                "floating_profit_pct":
                row[
                    "floating_profit_pct"
                ],

                "realized_profit":
                row[
                    "realized_profit"
                ],

                "total_score":
                total_score,

                "score_level":
                "A"
                if total_score >= 80
                else
                "B"
                if total_score >= 60
                else
                "C"
                if total_score >= 40
                else
                "D",

                "suggestion":
                self.get_suggestion(
                    total_score
                ),

                "update_time":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            })

        result = pd.DataFrame(
            result
        )

        result = result.sort_values(
            "total_score",
            ascending=False
        )

        return result

    # =====================================
    # 保存
    # =====================================

    def save_result(
        self,
        df
    ):

        conn = sqlite3.connect(
            self.db_path
        )

        conn.execute(
            """
            DELETE FROM
            dwd_etf_score
            """
        )

        df.to_sql(
            "dwd_etf_score",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # =====================================
    # 输出
    # =====================================

    def print_result(
        self,
        df
    ):

        print()

        print("=" * 100)
        print("ETF评分排行榜")
        print("=" * 100)

        for _, row in df.iterrows():

            print(

                f"{row['etf_code']} "

                f"{row['etf_name']:<10}"

                f" 分数:{row['total_score']:>3}"

                f" 等级:{row['score_level']}"

                f" 建议:{row['suggestion']}"

            )

    # =====================================
    # 主程序
    # =====================================

    def run(self):

        result = self.build_score()

        self.save_result(
            result
        )

        self.print_result(
            result
        )


if __name__ == "__main__":

    ETFScoreEngine().run()