-- ============================================================================
-- 表名: dwd_rebalance
-- 用途: ETF级别再平衡建议，对比实际仓位与目标仓位的偏离
-- 字段说明:
--   etf_code:       ETF代码 (主键)
--   etf_name:       ETF名称
--   category:        所属分类
--   current_value:   当前市值
--   current_pct:     当前占比
--   target_pct:      目标占比
--   deviation_pct:   偏离度
--   action:          操作建议 (加仓/减仓/持有)
--   update_time:     更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_rebalance;

CREATE TABLE dwd_rebalance (
    etf_code       TEXT PRIMARY KEY,
    etf_name       TEXT,
    category       TEXT,
    current_value  REAL,
    current_pct    REAL,
    target_pct     REAL,
    deviation_pct  REAL,
    action         TEXT,
    update_time    TEXT
);
