DROP TABLE IF EXISTS dwd_ai_decision;

CREATE TABLE dwd_ai_decision (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    signal_score REAL,

    allocation_pct REAL,

    floating_profit_pct REAL,

    ai_score REAL,

    ai_level TEXT,

    ai_action TEXT,

    ai_reason TEXT,

    update_time TEXT

);