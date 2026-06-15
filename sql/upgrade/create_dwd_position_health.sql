-- ============================================================================
-- 表名: dwd_position_health
-- 用途: 组合健康度检查，涵盖单ETF集中度/主题集中度/数量/重叠四项
-- 字段说明:
--   health_item: 检查项名称 (主键)
--   item_value:  检查值
--   risk_level:  风险等级 (危险/偏高/注意/正常)
--   suggestion:  改进建议
--   update_time: 更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_position_health;

CREATE TABLE dwd_position_health (
    health_item TEXT PRIMARY KEY,
    item_value  REAL,
    risk_level  TEXT,
    suggestion  TEXT,
    update_time TEXT
);
