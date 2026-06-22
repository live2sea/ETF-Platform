-- ============================================================================
-- 表名: dwd_macro_indicator
-- 用途: 宏观指标评分表，按日期对8个核心宏观指标打分并判断趋势方向
-- 字段说明:
--   indicator_date:  指标日期
--   indicator_name:  指标名称
--   indicator_value: 当前值
--   score:           指标评分 (0-100)
--   trend:           趋势方向 (上升/下降/持平)
--   comment:         评分说明
--   update_time:     更新时间
--   主键:            (indicator_date, indicator_name)
-- ============================================================================

DROP TABLE IF EXISTS dwd_macro_indicator;

CREATE TABLE dwd_macro_indicator (
    indicator_date  TEXT,
    indicator_name  TEXT,
    indicator_value REAL,
    score           INTEGER,
    trend           TEXT,
    comment         TEXT,
    update_time     TEXT,
    PRIMARY KEY (indicator_date, indicator_name)
);
