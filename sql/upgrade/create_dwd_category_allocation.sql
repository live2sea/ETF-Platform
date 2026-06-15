-- ============================================================================
-- 表名: dwd_category_allocation
-- 用途: 按国家/主题分类汇总仓位占比与风险等级
-- 字段说明:
--   category_name:  分类名称 (主键)
--   market_value:    分类总市值
--   allocation_pct:  分类占比 (%)
--   etf_count:       该分类下ETF数量
--   risk_level:      风险等级 (高/中/低)
--   update_time:     更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_category_allocation;

CREATE TABLE dwd_category_allocation (
    category_name  TEXT PRIMARY KEY,
    market_value   REAL,
    allocation_pct REAL,
    etf_count      INTEGER,
    risk_level     TEXT,
    update_time    TEXT
);
