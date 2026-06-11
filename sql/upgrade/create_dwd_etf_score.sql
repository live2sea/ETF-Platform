
--=========================================
-- 综合评分表
--========================================= 
DROP TABLE IF EXISTS dwd_etf_score;

CREATE TABLE dwd_etf_score (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    category_name TEXT,

    allocation_pct REAL,

    floating_profit REAL,

    floating_profit_pct REAL,

    realized_profit REAL,

    total_score INTEGER,

    score_level TEXT,

    suggestion TEXT,

    update_time TEXT

);