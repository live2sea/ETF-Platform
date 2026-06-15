import sqlite3
import pandas as pd

from datetime import datetime


class ETFScoreEngineV2:
    """
    ETF评分系统 V2

    评分构成：

    趋势评分(MA)         30
    RSI评分             20
    仓位健康度评分       20
    浮盈评分            15
    已实现收益评分       15

    总分 100
    """

    def __init__(self):

        self.db_path = "data/etf.db"

    # ==================================================
    # ETF分类映射
    # ==================================================

    def get_category(self, code):

        mapping = {

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

            "164824": "印度",

            "513000": "日本",
            "513800": "日本",

            "159865": "农业",

            "512170": "医疗",

            "159529": "消费",

            "159561": "欧洲"

        }

        return mapping.get(code, "其它")

    # ==================================================
    # 趋势评分（占位）
    # 后续接 MA20 MA60 MA120
    # ==================================================

    def calc_trend_score(self):

        return 15

    # ==================================================
    # RSI评分（占位）
    # 后续接 RSI指标
    # ==================================================

    def calc_rsi_score(self):

        return 10

    # ==================================================
    # 仓位评分
    # ==================================================

    def calc_allocation_score(self, allocation_pct):

        if allocation_pct <= 5:
            return 20

        elif allocation_pct <= 10:
            return 15

        elif allocation_pct <= 20:
            return 10

        elif allocation_pct <= 30:
            return 5

        return 0

    # ==================================================
    # 浮盈评分
    # ==================================================

    def calc_floating_score(self, profit_pct):

        if profit_pct >= 15:
            return 15

        elif profit_pct >= 5:
            return 12

        elif profit_pct >= 0:
            return 10

        elif profit_pct >= -10:
            return 6

        elif profit_pct >= -20:
            return 3

        return 0

    # ==================================================
    # 已实现收益评分
    # ==================================================

    def calc_realized_score(self, realized_profit):

        if realized_profit >= 5000:
            return 15

        elif realized_profit >= 2000:
            return 12

        elif realized_profit > 0:
            return 8

        return 3

    # ==================================================
    # 等级
    # ==================================================

    def get_level(self, score):

        if score >= 80:
            return "A"

        elif score >= 65:
            return "B"

        elif score >= 50:
            return "C"

        return "D"

    # ==================================================
    # 操作建议
    # ==================================================

    def get_suggestion(self, score):

        if score >= 80:
            return "优先加仓"

        elif score >= 65:
            return "继续持有"

        elif score >= 50:
            return "观察"

        return "减仓观察"

    # ==================================================
    # 读取数据
    # ==================================================

    def load_data(self):

        conn = sqlite3.connect(self.db_path)

        allocation = pd.read_sql("""

        SELECT
            etf_code,
            etf_name,
            allocation_pct
        FROM dwd_allocation

        """, conn)

        floating = pd.read_sql("""

        SELECT
            etf_code,
            floating_profit,
            floating_profit_pct
        FROM dwd_floating_profit

        """, conn)

        profit = pd.read_sql("""

        SELECT
            etf_code,
            realized_profit
        FROM dwd_profit_analysis

        """, conn)

        conn.close()

        return allocation, floating, profit

    # ==================================================
    # 创建目标表
    # ==================================================

    def create_table(self):

        conn = sqlite3.connect(self.db_path)

        conn.execute("""

        CREATE TABLE IF NOT EXISTS dwd_etf_score_v2 (

            etf_code TEXT PRIMARY KEY,

            etf_name TEXT,

            category_name TEXT,

            allocation_pct REAL,

            floating_profit REAL,

            floating_profit_pct REAL,

            realized_profit REAL,

            trend_score INTEGER,

            rsi_score INTEGER,

            allocation_score INTEGER,

            floating_score INTEGER,

            realized_score INTEGER,

            total_score INTEGER,

            score_level TEXT,

            suggestion TEXT,

            update_time TEXT

        )

        """)

        conn.commit()

        conn.close()

    # ==================================================
    # 核心评分计算
    # ==================================================

    def build_score(self):

        allocation, floating, profit = self.load_data()

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

        df.fillna(0, inplace=True)

        result = []

        for _, row in df.iterrows():

            trend_score = self.calc_trend_score()

            rsi_score = self.calc_rsi_score()

            allocation_score = self.calc_allocation_score(
                row["allocation_pct"]
            )

            floating_score = self.calc_floating_score(
                row["floating_profit_pct"]
            )

            realized_score = self.calc_realized_score(
                row["realized_profit"]
            )

            total_score = (
                trend_score
                + rsi_score
                + allocation_score
                + floating_score
                + realized_score
            )

            result.append({

                "etf_code":
                    row["etf_code"],

                "etf_name":
                    row["etf_name"],

                "category_name":
                    self.get_category(
                        row["etf_code"]
                    ),

                "allocation_pct":
                    round(row["allocation_pct"], 2),

                "floating_profit":
                    round(row["floating_profit"], 2),

                "floating_profit_pct":
                    round(row["floating_profit_pct"], 2),

                "realized_profit":
                    round(row["realized_profit"], 2),

                "trend_score":
                    trend_score,

                "rsi_score":
                    rsi_score,

                "allocation_score":
                    allocation_score,

                "floating_score":
                    floating_score,

                "realized_score":
                    realized_score,

                "total_score":
                    total_score,

                "score_level":
                    self.get_level(
                        total_score
                    ),

                "suggestion":
                    self.get_suggestion(
                        total_score
                    ),

                "update_time":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
            })

        result = pd.DataFrame(result)

        result = result.sort_values(
            "total_score",
            ascending=False
        )

        return result

    # ==================================================
    # 保存结果
    # ==================================================

    def save_result(self, result):

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            "DELETE FROM dwd_etf_score_v2"
        )

        result.to_sql(
            "dwd_etf_score_v2",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # ==================================================
    # 打印结果
    # ==================================================

    def print_result(self, result):

        print()
        print("=" * 100)
        print("ETF评分V2排行榜")
        print("=" * 100)

        for _, row in result.iterrows():

            print(

                f"{row['etf_code']} "
                f"{row['etf_name']:<10}"

                f" 总分:{row['total_score']:>3}"

                f" 等级:{row['score_level']}"

                f" 建议:{row['suggestion']}"

            )

    # ==================================================
    # 主程序
    # ==================================================

    def run(self):

        self.create_table()

        result = self.build_score()

        self.save_result(result)

        self.print_result(result)


if __name__ == "__main__":

    ETFScoreEngineV2().run()