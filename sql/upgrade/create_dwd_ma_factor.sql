-- ============================================================================
-- 表名: dwd_ma_factor
-- 用途: MA均线技术指标因子 (MA20/MA60/MA120/MA250)
-- 字段说明:
--   etf_code:     ETF代码 (主键)
--   etf_name:     ETF名称
--   trade_date:   最新交易日期
--   close_price:  收盘价
--   ma20:         20日均线
--   ma60:         60日均线
--   ma120:        120日均线
--   ma250:        250日均线
--   trend_score:  趋势评分 (0-100)
--   trend_level:  趋势等级 (S/A/B/C/D)
--   signal:       操作信号
--   update_time:  更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_ma_factor;

CREATE TABLE dwd_ma_factor (
    etf_code     TEXT PRIMARY KEY,
    etf_name     TEXT,
    trade_date   TEXT,
    close_price  REAL,
    ma20         REAL,
    ma60         REAL,
    ma120        REAL,
    ma250        REAL,
    trend_score  INTEGER,
    trend_level  TEXT,
    signal       TEXT,
    update_time  TEXT
);
