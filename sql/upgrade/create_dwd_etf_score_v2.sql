-- ============================================================================
-- 表名: dwd_etf_score_v2
-- 用途: ETF综合评分V2，基于仓位/浮动盈亏/已实现收益计算综合评分
-- 字段说明:
--   etf_code:            ETF代码 (主键)
--   etf_name:            ETF名称
--   category_name:        分类名称
--   allocation_pct:       仓位占比
--   floating_profit:      浮动盈亏
--   floating_profit_pct:  浮动盈亏百分比
--   realized_profit:      已实现盈亏
--   total_score:          综合总分
--   score_level:          评分等级 (A/B/C/D)
--   suggestion:           操作建议
--   update_time:          更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_etf_score_v2;

CREATE TABLE dwd_etf_score_v2 (
    etf_code            TEXT PRIMARY KEY,
    etf_name            TEXT,
    category_name       TEXT,
    allocation_pct      REAL,
    floating_profit     REAL,
    floating_profit_pct REAL,
    realized_profit     REAL,
    total_score         INTEGER,
    score_level         TEXT,
    suggestion          TEXT,
    update_time         TEXT
);
