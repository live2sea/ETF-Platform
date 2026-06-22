-- ============================================================================
-- 表名: ods_macro_indicator
-- 用途: 宏观指标原始数据表，存储从AKShare拉取的8个核心宏观指标原始值
-- 字段说明:
--   id:              自增主键
--   indicator_date:  指标日期
--   indicator_name:  指标名称 (PMI/M2/CPI/PPI/中美利差/美联储利率/沪深300PE/北向资金)
--   indicator_value: 指标原始值
--   source:          数据来源
--   update_time:     更新时间
-- ============================================================================

DROP TABLE IF EXISTS ods_macro_indicator;

CREATE TABLE ods_macro_indicator (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_date  TEXT,
    indicator_name  TEXT,
    indicator_value REAL,
    source          TEXT,
    update_time     TEXT
);

CREATE INDEX IF NOT EXISTS idx_ods_macro_date_name
    ON ods_macro_indicator (indicator_date, indicator_name);
