
--==========================================
-- 浮盈浮亏分析表

DROP TABLE IF EXISTS dwd_floating_profit;

CREATE TABLE dwd_floating_profit (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    quantity INTEGER,

    avg_cost REAL,

    current_price REAL,

    cost_value REAL,

    market_value REAL,

    floating_profit REAL,

    floating_profit_pct REAL,

    update_time TEXT

);