-- ============================================================================
-- 表名: dwd_etf_overlap
-- 用途: ETF重叠分析，检测同一主题下多只ETF重复持仓的风险
-- 字段说明:
--   group_name:      分组名称
--   etf_count:       组内ETF数量
--   total_value:     组内总市值
--   allocation_pct:  组内占比
--   risk_level:      风险等级 (危险/注意/正常)
--   suggestion:      处理建议
--   update_time:     更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_etf_overlap;

CREATE TABLE dwd_etf_overlap (
    group_name      TEXT,
    etf_count       INTEGER,
    total_value     REAL,
    allocation_pct  REAL,
    risk_level      TEXT,
    suggestion      TEXT,
    update_time     TEXT
);
