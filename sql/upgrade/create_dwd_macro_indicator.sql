-- ============================================================================
-- 表名: dwd_macro_indicator
-- 用途: 宏观指标汇总表
--
-- 指标包括:
--   PMI
--   社会融资规模增速
--   美联储利率
--   美国10年国债收益率
--   美元指数(DXY)
--
-- 字段说明:
--   indicator_name  : 指标名称
--   indicator_value : 当前值
--   trend           : 趋势
--   score           : 指标评分
--   comment         : AI解释
--   update_time     : 更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_macro_indicator;

CREATE TABLE dwd_macro_indicator (

    indicator_name TEXT PRIMARY KEY,

    indicator_value REAL,

    trend TEXT,

    score INTEGER,

    comment TEXT,

    update_time TEXT

);