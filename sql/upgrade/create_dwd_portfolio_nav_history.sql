-- ============================================================================
-- 表名: dwd_portfolio_nav_history
-- 用途: 账户净值历史记录，每日计算总成本、总市值、总盈亏和收益率
-- 字段说明:
--   trade_date:   交易日期 (主键)
--   total_cost:   总成本
--   total_market: 总市值
--   total_profit: 总盈亏
--   profit_pct:   收益率 (%)
--   update_time:  更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_portfolio_nav_history;

CREATE TABLE dwd_portfolio_nav_history (
    trade_date   TEXT PRIMARY KEY,
    total_cost   REAL,
    total_market REAL,
    total_profit REAL,
    profit_pct   REAL,
    update_time  TEXT
);
