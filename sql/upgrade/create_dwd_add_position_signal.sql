-- ============================================================================
-- 表名: dwd_add_position_signal
-- 用途: 加仓建议信号，综合信号/仓位/浮亏计算加仓推荐
-- 字段说明:
--   etf_code:            ETF代码 (主键)
--   etf_name:            ETF名称
--   signal_score:         综合信号得分
--   floating_score:       浮亏得分
--   allocation_score:     仓位得分
--   final_score:          最终综合分
--   allocation_pct:       仓位占比
--   floating_profit_pct:  浮动盈亏百分比
--   recommend_amount:     建议加仓金额
--   recommendation:       加仓建议文字
--   update_time:          更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_add_position_signal;

CREATE TABLE dwd_add_position_signal (
    etf_code            TEXT PRIMARY KEY,
    etf_name            TEXT,
    signal_score        REAL,
    floating_score      REAL,
    allocation_score    REAL,
    final_score         REAL,
    allocation_pct      REAL,
    floating_profit_pct REAL,
    recommend_amount    REAL,
    recommendation      TEXT,
    update_time         TEXT
);

CREATE INDEX IF NOT EXISTS idx_add_position_score
    ON dwd_add_position_signal (final_score DESC);
