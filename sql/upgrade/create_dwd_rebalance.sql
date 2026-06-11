DROP TABLE IF EXISTS dwd_rebalance;

CREATE TABLE dwd_rebalance
(
    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    category TEXT,

    current_value REAL,
    current_pct REAL,

    target_pct REAL,

    deviation_pct REAL,

    action TEXT,

    update_time TEXT
);