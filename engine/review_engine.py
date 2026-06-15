# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd

from datetime import datetime


class ReviewEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    # =====================================
    # Dashboard数据
    # =====================================

    def load_dashboard(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                item_name,
                item_value
            FROM dwd_dashboard
            """,
            conn
        )

        conn.close()

        return df

    # =====================================
    # ETF评分
    # =====================================

    def load_signal(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                etf_code,
                etf_name,
                signal_score
            FROM dwd_etf_signal
            """,
            conn
        )

        conn.close()

        return df

    # =====================================
    # 风险分析
    # =====================================

    def load_risk(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                risk_level
            FROM dwd_risk_analysis
            """,
            conn
        )

        conn.close()

        return df

    # =====================================
    # 加仓建议
    # =====================================

    def load_add_position(self):

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql(
            """
            SELECT
                etf_code,
                etf_name,
                final_score,
                recommend_amount
            FROM dwd_add_position_signal
            ORDER BY final_score DESC
            """,
            conn
        )

        conn.close()

        return df

    # =====================================
    # 生成复盘
    # =====================================

    def build_review(self):

        dashboard_df = self.load_dashboard()

        signal_df = self.load_signal()

        risk_df = self.load_risk()

        add_df = self.load_add_position()

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        rows = []

        # ------------------------
        # Dashboard指标
        # ------------------------

        dashboard_map = dict(
            zip(
                dashboard_df["item_name"],
                dashboard_df["item_value"]
            )
        )

        total_value = dashboard_map.get(
            "总市值",
            "-"
        )

        total_profit = dashboard_map.get(
            "总盈亏",
            "-"
        )

        profit_pct = dashboard_map.get(
            "收益率",
            "-"
        )

        rows.append([
            "总资产",
            total_value,
            now
        ])

        rows.append([
            "总盈亏",
            total_profit,
            now
        ])

        rows.append([
            "收益率",
            profit_pct,
            now
        ])

        # ------------------------
        # 最佳ETF
        # ------------------------

        if not signal_df.empty:

            best = signal_df.sort_values(
                "signal_score",
                ascending=False
            ).iloc[0]

            worst = signal_df.sort_values(
                "signal_score",
                ascending=True
            ).iloc[0]

            rows.append([
                "最佳ETF",
                f"{best['etf_code']} {best['etf_name']}",
                now
            ])

            rows.append([
                "最差ETF",
                f"{worst['etf_code']} {worst['etf_name']}",
                now
            ])

        # ------------------------
        # 推荐加仓
        # ------------------------

        if not add_df.empty:

            top_add = add_df.iloc[0]

            rows.append([
                "推荐加仓",
                f"{top_add['etf_code']} {top_add['etf_name']}",
                now
            ])

        # ------------------------
        # 风险数量
        # ------------------------

        risk_count = len(
            risk_df[
                risk_df["risk_level"].isin(
                    ["高", "HIGH"]
                )
            ]
        )

        rows.append([
            "高风险项数量",
            str(risk_count),
            now
        ])

        # ------------------------
        # AI总结
        # ------------------------

        best_name = ""

        if not signal_df.empty:

            best_name = best["etf_name"]

        summary = (
            f"当前组合收益率{profit_pct}，"
            f"最佳ETF为{best_name}，"
            f"当前高风险项{risk_count}个，"
            f"建议优先关注综合评分靠前ETF。"
        )

        rows.append([
            "AI总结",
            summary,
            now
        ])

        review_df = pd.DataFrame(
            rows,
            columns=[
                "review_item",
                "review_value",
                "update_time"
            ]
        )

        return review_df

    # =====================================
    # 保存
    # =====================================

    def save(self, df):

        conn = sqlite3.connect(self.db_path)

        conn.execute(
            "DELETE FROM dwd_daily_review"
        )

        df.to_sql(
            "dwd_daily_review",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

        conn.close()

    # =====================================
    # 主流程
    # =====================================

    def run(self):

        review_df = self.build_review()

        self.save(review_df)

        print()
        print("=" * 80)
        print("ETF每日复盘")
        print("=" * 80)

        for _, row in review_df.iterrows():

            print(
                f"{row['review_item']:<10}"
                f" : "
                f"{row['review_value']}"
            )


if __name__ == "__main__":

    ReviewEngine().run()