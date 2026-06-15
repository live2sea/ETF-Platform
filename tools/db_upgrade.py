# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

DB_PATH = "data/etf.db"
UPGRADE_DIR = "sql/upgrade"


def execute_sql_file(conn, sql_file):

    print(f"执行: {sql_file.name}")

    with open(sql_file, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def main():

    conn = sqlite3.connect(DB_PATH)

    try:

        sql_files = sorted(
            Path(UPGRADE_DIR).glob("create_dwd_signal_trend.sql")
        )

        for sql_file in sql_files:
            execute_sql_file(
                conn,
                sql_file
            )

        conn.commit()

        print("\n数据库升级完成")

    finally:

        conn.close()


if __name__ == "__main__":
    main()