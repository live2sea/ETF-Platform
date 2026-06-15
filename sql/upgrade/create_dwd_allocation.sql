-- ============================================================================
-- 表名: dwd_allocation
-- 用途: ETF实时仓位结构，计算每只ETF的市值占比
-- 字段说明:
--   etf_code:       ETF代码 (主键)
--   etf_name:       ETF名称
--   quantity:        持仓数量
--   avg_cost:        平均成本
--   current_price:   当前价格
--   cost_value:      成本市值
--   market_value:    当前市值
--   allocation_pct:  仓位占比 (%)
--   update_time:     更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_allocation;

CREATE TABLE dwd_allocation (
    etf_code       TEXT PRIMARY KEY,
    etf_name       TEXT,
    quantity       INTEGER,
    avg_cost       REAL,
    current_price  REAL,
    cost_value     REAL,
    market_value   REAL,
    allocation_pct REAL,
    update_time    TEXT
);
