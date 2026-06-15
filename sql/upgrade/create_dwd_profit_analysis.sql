-- ============================================================================
-- 表名: dwd_profit_analysis
-- 用途: 已实现盈亏分析，按收益排序生成排名
-- 字段说明:
--   etf_code:        ETF代码 (主键)
--   etf_name:        ETF名称
--   quantity:         持仓数量
--   avg_cost:         平均成本
--   realized_profit:  已实现盈亏
--   profit_rank:      收益排名
--   update_time:      更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_profit_analysis;

CREATE TABLE dwd_profit_analysis (
    etf_code        TEXT PRIMARY KEY,
    etf_name        TEXT,
    quantity        INTEGER,
    avg_cost        REAL,
    realized_profit REAL,
    profit_rank     INTEGER,
    update_time     TEXT
);
