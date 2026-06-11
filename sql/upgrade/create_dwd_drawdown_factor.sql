DROP TABLE IF EXISTS dwd_drawdown_factor;

CREATE TABLE dwd_drawdown_factor
(
    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    current_price REAL,

    high_52w REAL,

    low_52w REAL,

    drawdown_pct REAL,

    score INTEGER,

    level TEXT,

    signal TEXT,

    update_time TEXT
);