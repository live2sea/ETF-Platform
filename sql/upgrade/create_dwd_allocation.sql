-- =====================================
-- 当前仓位结构分析表
-- =====================================

DROP TABLE IF EXISTS dwd_allocation;

CREATE TABLE dwd_allocation (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    quantity INTEGER,

    avg_cost REAL,

    current_price REAL,

    cost_value REAL,

    market_value REAL,

    allocation_pct REAL,

    update_time TEXT

);
