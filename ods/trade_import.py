#!/usr/bin/env python3
# 解释：该脚本定义了一个TradeImporter类，用于从Excel文件中导入ETF交易记录。
# 它包含方法来加载Excel数据、过滤出ETF相关的记录、转换列名以适应数据库结构，并将数据保存到SQLite数据库中。
# 最后，在主程序中创建一个TradeImporter实例并运行导入过程。
import pandas as pd
import sqlite3
import os
import shutil


class TradeImporter:

    def __init__(self):

        self.db_path = "data/etf.db"

    def load_excel(self, file_path):

        df = pd.read_excel(file_path)

        return df

    def filter_etf(self, df):

        # 转字符串
        df["证券代码"] = df["证券代码"].astype(str)

        # 保留ETF/LOF
        etf_prefix = (
            "15",   # 深市ETF
            "16",   # LOF
            "51",   # 沪市ETF
            "56"    # 沪市ETF
        )

        df = df[
            df["证券代码"].str.startswith(etf_prefix)
        ]

        return df

    def transform(self, df):

        df = df.rename(columns={

            "成交日期": "trade_date",
            "成交时间": "trade_time",

            "证券代码": "etf_code",
            "证券名称": "etf_name",

            "买卖标志": "trade_type",

            "成交数量": "quantity",
            "成交价格": "price",
            "成交金额": "amount",

            "手续费": "fee",
            "印花税": "tax",

            "清算金额": "settlement_amount"

        })

        return df[
            [
                "trade_date",
                "trade_time",
                "etf_code",
                "etf_name",
                "trade_type",
                "quantity",
                "price",
                "amount",
                "fee",
                "tax",
                "settlement_amount"
            ]
        ]

    def save_sqlite(self, df):
        dedup_cols = ["trade_date", "trade_time", "etf_code",
                      "trade_type", "price", "quantity"]

        conn = sqlite3.connect(self.db_path)

        try:
            existing = pd.read_sql(
                f"SELECT {', '.join(dedup_cols)} FROM ods_trade_record",
                conn
            )
            existing_keys = set(
                tuple(row[col] for col in dedup_cols)
                for _, row in existing.iterrows()
            )
        except Exception:
            existing_keys = set()

        new_rows = []
        for _, row in df.iterrows():
            key = tuple(row[col] for col in dedup_cols)
            if key not in existing_keys:
                new_rows.append(row)

        new_df = pd.DataFrame(new_rows, columns=df.columns)

        if len(new_df) > 0:
            # Use INSERT OR IGNORE as safety net against the unique index
            cols = ", ".join(new_df.columns)
            placeholders = ", ".join(["?"] * len(new_df.columns))
            sql = f"INSERT OR IGNORE INTO ods_trade_record ({cols}) VALUES ({placeholders})"
            conn.executemany(sql, new_df.values.tolist())

        skipped = len(df) - len(new_df)
        conn.commit()
        conn.close()

        print(f"导入 {len(new_df)} 条新记录，跳过 {skipped} 条重复")

    def run(self, file_path):

        df = self.load_excel(file_path)

        df = self.filter_etf(df)

        df = self.transform(df)

        self.save_sqlite(df)


if __name__ == "__main__":

    importer = TradeImporter()

    importer.run(
        "data/jylv_20260609.xlsx"
    )