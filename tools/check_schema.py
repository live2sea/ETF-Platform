# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd


class CheckSchema:

    def __init__(self):

        self.db_path = "data/etf.db"

    def get_tables(self):

        conn = sqlite3.connect(self.db_path)

        try:

            tables = pd.read_sql(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                ORDER BY name
                """,
                conn
            )

        finally:
            conn.close()

        return tables["name"].tolist()

    def get_columns(self, table_name):

        conn = sqlite3.connect(self.db_path)

        try:

            cursor = conn.execute(
                f"PRAGMA table_info({table_name})"
            )

            columns = cursor.fetchall()

        finally:
            conn.close()

        return columns

    def print_table(self, table_name):

        print()
        print("=" * 80)
        print(table_name)
        print("=" * 80)

        columns = self.get_columns(table_name)

        for col in columns:

            cid = col[0]
            name = col[1]
            col_type = col[2]
            pk = col[5]

            print(
                f"{cid:2} | "
                f"{name:25} | "
                f"{col_type:10} | "
                f"PK={pk}"
            )

    def summary(self):

        tables = self.get_tables()

        print()
        print("=" * 80)
        print("ETF数据库结构总览")
        print("=" * 80)

        print()
        print(f"表数量：{len(tables)}")

        print()
        print("ODS层")
        print("-" * 40)

        for table in tables:

            if table.startswith("ods_"):

                print(table)

        print()
        print("DWD层")
        print("-" * 40)

        for table in tables:

            if table.startswith("dwd_"):

                print(table)

        print()
        print("其它表")
        print("-" * 40)

        for table in tables:

            if (
                not table.startswith("ods_")
                and not table.startswith("dwd_")
            ):

                print(table)

    def run(self):

        tables = self.get_tables()

        self.summary()

        print()
        print("=" * 80)
        print("字段详情")
        print("=" * 80)

        for table in tables:

            self.print_table(table)


if __name__ == "__main__":

    CheckSchema().run()