-- ============================================================================
-- 表名: dwd_floating_profit
-- 用途: 浮动盈亏分析，合并持仓与行情计算浮动盈亏
-- 字段说明:
--   etf_code:            ETF代码 (主键)
--   etf_name:            ETF名称
--   quantity:             持仓数量
--   avg_cost:             平均成本
--   current_price:        当前价格
--   cost_value:           成本市值
--   market_value:         当前市值
--   floating_profit:      浮动盈亏
--   floating_profit_pct:  浮动盈亏百分比
--   update_time:          更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_floating_profit;

CREATE TABLE dwd_floating_profit (
    etf_code            TEXT PRIMARY KEY,
    etf_name            TEXT,
    quantity            INTEGER,
    avg_cost            REAL,
    current_price       REAL,
    cost_value          REAL,
    market_value        REAL,
    floating_profit     REAL,
    floating_profit_pct REAL,
    update_time         TEXT
);
