DROP TABLE IF EXISTS dwd_rsi_factor;

CREATE TABLE dwd_rsi_factor
(
    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    current_price REAL,

    rsi6 REAL,
    rsi12 REAL,
    rsi24 REAL,

    score INTEGER,

    level TEXT,

    signal TEXT,

    update_time TEXT
);