DROP TABLE IF EXISTS dwd_etf_score_v2;
CREATE TABLE dwd_etf_score_v2 (
    etf_code            TEXT PRIMARY KEY,
    etf_name            TEXT,
    category_name       TEXT,
    allocation_pct      REAL,
    floating_profit     REAL,
    floating_profit_pct REAL,
    realized_profit     REAL,
    macro_bonus         INTEGER,
    total_score         INTEGER,
    score_level         TEXT,
    suggestion          TEXT,
    update_time         TEXT
);
