
--### 建表语句 sqlite3 data/etf.db < sql/upgrade/create_dwd_ma_factor.sql
--### DWD层：MA技术指标数据表
--### 2024-06-01

DROP TABLE IF EXISTS dwd_ma_factor;

CREATE TABLE dwd_ma_factor (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    trade_date TEXT,

    close_price REAL,

    ma20 REAL,

    ma60 REAL,

    ma120 REAL,

    ma250 REAL,

    trend_score INTEGER,

    trend_level TEXT,

    signal TEXT,

    update_time TEXT

);