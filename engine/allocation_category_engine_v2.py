import sqlite3
import pandas as pd

from datetime import datetime


class AllocationCategoryEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

        # ==========================
        # ETF分类映射
        # 后续可以迁移数据库配置表
        # ==========================

        self.category_map = {

            # 港股科技

            "159740": "港股科技",
            "513580": "港股科技",
            "513980": "港股科技",

            # 美股科技

            "159632": "美股科技",
            "159696": "美股科技",
            "513300": "美股科技",
            "513110": "美股科技",
            "159659": "美股科技",

            # 美股宽基

            "513400": "美股宽基",

            # 红利

            "510880": "红利",
            "563020": "红利",

            # 日本

            "513000": "日本",
            "513800": "日本",

            # 欧洲

            "159561": "欧洲",

            # 印度

            "164824": "印度",

            # 医疗

            "512170": "医疗",

            # 农业

            "159865": "农业",

            # 消费

            "159529": "消费"

        }

    # =====================================================
    # 读取实时仓位表
    # =====================================================

    def load_allocation(self):

        conn = sqlite3.connect(
            self.db_path
        )

        sql = """
        select
            etf_code,
            etf_name,
            market_value
        from dwd_allocation
        """

        df = pd.read_sql(
            sql,
            conn
        )

        conn.close()

        df["etf_code"] = (
            df["etf_code"]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.strip()
            .str.zfill(6)
        )

        df["market_value"] = pd.to_numeric(
            df["market_value"],
            errors="coerce"
        )

        return df

    # =====================================================
    # 风险等级
    # =====================================================

    def get_risk_level(self, pct):

        if pct >= 35:

            return "高风险"

        elif pct >= 20:

            return "中风险"

        else:

            return "低风险"

    # =====================================================
    # 分类汇总
    # =====================================================

    def build_category(self):

        df = self.load_allocation()

        if len(df) == 0:

            print("dwd_allocation为空")

            return pd.DataFrame()

        # =====================
        # 去掉空市值
        # =====================

        df = df.dropna(
            subset=["market_value"]
        )

        total_market_value = (
            df["market_value"]
            .sum()
        )

        if total_market_value <= 0:

            print(
                "总市值异常，请检查 dwd_allocation"
            )

            return pd.DataFrame()

        # =====================
        # 分类
        # =====================

        df["category_name"] = (
            df["etf_code"]
            .map(self.category_map)
        )

        # =====================
        # 未配置ETF
        # =====================

        unknown = df[
            df["category_name"].isna()
        ]

        if len(unknown) > 0:

            print()

            print("=" * 80)
            print("发现未分类ETF")
            print("=" * 80)

            print(
                unknown[
                    [
                        "etf_code",
                        "etf_name"
                    ]
                ]
            )

            print()

            df["category_name"] = (
                df["category_name"]
                .fillna("其它")
            )

        # =====================
        # 聚合
        # =====================

        result = (
            df.groupby(
                "category_name",
                as_index=False
            )
            .agg(
                market_value=(
                    "market_value",
                    "sum"
                ),
                etf_count=(
                    "etf_code",
                    "count"
                )
            )
        )

        result["allocation_pct"] = (
            result["market_value"]
            / total_market_value
            * 100
        ).round(2)

        result["risk_level"] = (
            result["allocation_pct"]
            .apply(
                self.get_risk_level
            )
        )

        result["update_time"] = (
            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        result = result.sort_values(
            "allocation_pct",
            ascending=False
        )

        return result

    # =====================================================
    # 保存
    # =====================================================

    def save_result(self, result):

        if len(result) == 0:

            return

        conn = sqlite3.connect(
            self.db_path
        )

        conn.execute(
            """
            DELETE FROM
            dwd_category_allocation
            """
        )

        result.to_sql(
            "dwd_category_allocation",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # =====================================================
    # 输出
    # =====================================================

    def print_result(self, result):

        if len(result) == 0:

            return

        total_market_value = (
            result["market_value"]
            .sum()
        )

        print()

        print("=" * 90)
        print("国家 / 主题仓位分析")
        print("=" * 90)

        print()

        print(
            f"总市值：{total_market_value:,.2f}"
        )

        print()

        for _, row in result.iterrows():

            print(

                f"{row['category_name']:<10}"

                f"市值:{row['market_value']:>12.2f}"

                f" 占比:{row['allocation_pct']:>6.2f}%"

                f" ETF数:{row['etf_count']:>2}"

                f" 风险:{row['risk_level']}"
            )

    # =====================================================
    # 主程序
    # =====================================================

    def run(self):

        result = self.build_category()

        self.save_result(
            result
        )

        self.print_result(
            result
        )


if __name__ == "__main__":

    AllocationCategoryEngine().run()