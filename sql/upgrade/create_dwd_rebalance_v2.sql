-- ============================================================================
-- 表名: dwd_rebalance_v2
-- 用途: 主题级别再平衡建议V2，按分类汇总计算调整金额
-- 字段说明:
--   category:        分类名称 (主键)
--   current_value:   当前市值
--   current_pct:     当前占比
--   target_pct:      目标占比
--   deviation_pct:   偏离度
--   action:          操作建议 (加仓/减仓/持有)
--   suggest_amount:  建议调整金额
--   update_time:     更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_rebalance_v2;

CREATE TABLE dwd_rebalance_v2 (
    category        TEXT PRIMARY KEY,
    current_value   REAL,
    current_pct     REAL,
    target_pct      REAL,
    deviation_pct   REAL,
    action          TEXT,
    suggest_amount  REAL,
    update_time     TEXT
);
