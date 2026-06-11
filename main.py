#!/usr/bin/env python3
#解释：该脚本用于初始化数据库。它连接到一个SQLite数据库，执行一个SQL脚本来创建必要的表和结构，然后关闭连接并打印完成消息。
import sqlite3

conn = sqlite3.connect(
    "data/etf.db"
)

cursor = conn.cursor()

with open(
    "sql/init_db.sql",
    "r",
    encoding="utf-8"
) as f:

    cursor.executescript(f.read())

conn.commit()

conn.close()

print("数据库初始化完成")