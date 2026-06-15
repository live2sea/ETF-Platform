-- ============================================================================
-- 表名: dwd_rsi_factor
-- 用途: RSI相对强弱指标因子 (RSI6/RSI12/RSI24)
-- 字段说明:
--   etf_code:      ETF代码 (主键)
--   etf_name:      ETF名称
--   current_price:  当前价格
--   rsi6:          6日RSI
--   rsi12:         12日RSI
--   rsi24:         24日RSI
--   score:         RSI评分 (0-100)
--   level:         等级 (S/A/B/C/D)
--   signal:        操作信号
--   update_time:   更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_rsi_factor;

CREATE TABLE dwd_rsi_factor (
    etf_code      TEXT PRIMARY KEY,
    etf_name      TEXT,
    current_price REAL,
    rsi6          REAL,
    rsi12         REAL,
    rsi24         REAL,
    score         INTEGER,
    level         TEXT,
    signal        TEXT,
    update_time   TEXT
);
