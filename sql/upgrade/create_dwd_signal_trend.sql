-- ============================================================================
-- 表名: dwd_signal_trend
-- 用途: 信号趋势分析，对比今日与昨日信号评分的变化方向
-- 字段说明:
--   etf_code:        ETF代码 (主键)
--   etf_name:        ETF名称
--   today_score:     今日评分
--   yesterday_score: 昨日评分
--   change_score:     评分变化
--   trend:            趋势描述 (显著增强/增强/持平/走弱/显著走弱)
--   update_time:      更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_signal_trend;

CREATE TABLE dwd_signal_trend (
    etf_code        TEXT PRIMARY KEY,
    etf_name        TEXT,
    today_score     REAL,
    yesterday_score REAL,
    change_score    REAL,
    trend           TEXT,
    update_time     TEXT
);
