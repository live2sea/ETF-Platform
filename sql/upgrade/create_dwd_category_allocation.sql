
-- ==========================================
-- 国家 / 主题仓位分析
-- ==========================================

DROP TABLE IF EXISTS dwd_category_allocation;
CREATE TABLE dwd_category_allocation (

    category_name TEXT PRIMARY KEY,

    market_value REAL,

    allocation_pct REAL,

    etf_count INTEGER,

    risk_level TEXT,

    update_time TEXT

);