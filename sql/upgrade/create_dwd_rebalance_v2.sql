DROP TABLE IF EXISTS dwd_rebalance_v2;

CREATE TABLE dwd_rebalance_v2
(
    category TEXT PRIMARY KEY,

    current_value REAL,
    current_pct REAL,

    target_pct REAL,

    deviation_pct REAL,

    action TEXT,

    suggest_amount REAL,

    update_time TEXT
);