-- ==========================================
-- dwd_add_position_signal
-- ETF加仓建议表
-- ==========================================

DROP TABLE IF EXISTS dwd_add_position_signal;

CREATE TABLE dwd_add_position_signal (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    signal_score REAL,

    floating_score REAL,

    allocation_score REAL,

    final_score REAL,

    allocation_pct REAL,

    floating_profit_pct REAL,

    recommend_amount REAL,

    recommendation TEXT,

    update_time TEXT

);

CREATE INDEX IF NOT EXISTS idx_add_position_score
ON dwd_add_position_signal(final_score DESC);