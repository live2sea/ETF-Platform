-- ============================================================================
-- 表名: dwd_risk_analysis
-- 用途: 组合风险分析，检测单只ETF和单一主题的集中度风险
-- 字段说明:
--   risk_type:   风险类型 (ETF/主题)
--   risk_name:   风险项名称
--   risk_value:  风险值 (占比)
--   risk_level:  风险等级 (高/中/低)
--   suggestion:  改进建议
--   update_time: 更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_risk_analysis;

CREATE TABLE dwd_risk_analysis (
    risk_type   TEXT,
    risk_name   TEXT,
    risk_value  REAL,
    risk_level  TEXT,
    suggestion  TEXT,
    update_time TEXT
);
