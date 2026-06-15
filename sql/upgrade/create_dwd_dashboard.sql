-- ============================================================================
-- 表名: dwd_dashboard
-- 用途: 仪表盘汇总快照，聚合账户总览/最佳ETF/推荐加仓/风险提示
-- 字段说明:
--   item_name:   指标名称 (主键)
--   item_value:  指标值
--   update_time: 更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_dashboard;

CREATE TABLE dwd_dashboard (
    item_name   TEXT PRIMARY KEY,
    item_value  TEXT,
    update_time TEXT
);
