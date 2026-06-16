-- ============================================================================
-- 表名: dwd_portfolio_nav_history
-- 用途: 账户净值历史记录
-- ============================================================================

DROP TABLE IF EXISTS dwd_portfolio_nav_history;

CREATE TABLE dwd_portfolio_nav_history (

    trade_date TEXT PRIMARY KEY,

    total_cost REAL,

    total_market REAL,

    total_profit REAL,

    profit_pct REAL,

    update_time TEXT

);