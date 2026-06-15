-- ============================================================================
-- 表名: dwd_position
-- 用途: 当前持仓快照，通过交易记录聚合计算得出
-- 字段说明:
--   etf_code:        ETF代码 (主键)
--   etf_name:        ETF名称
--   quantity:         持仓数量
--   avg_cost:         平均成本
--   buy_amount:       累计买入金额
--   sell_amount:      累计卖出金额
--   realized_profit:  已实现盈亏
--   update_time:      更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_position;

CREATE TABLE dwd_position (
    etf_code        TEXT PRIMARY KEY,
    etf_name        TEXT,
    quantity        INTEGER,
    avg_cost        REAL,
    buy_amount      REAL,
    sell_amount     REAL,
    realized_profit REAL,
    update_time     TEXT
);
