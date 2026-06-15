-- ============================================================================
-- 表名: ods_trade_record
-- 用途: 存储从券商平台导出的ETF原始交易记录
-- 字段说明:
--   id:                 自增主键
--   trade_date:         交易日期 (YYYY-MM-DD)
--   trade_time:         交易时间
--   etf_code:           ETF代码
--   etf_name:           ETF名称
--   trade_type:         交易类型 (买入/卖出)
--   quantity:           交易数量
--   price:              成交价格
--   amount:             成交金额
--   fee:                手续费
--   tax:                税费
--   settlement_amount:  结算金额
-- ============================================================================

DROP TABLE IF EXISTS ods_trade_record;

CREATE TABLE ods_trade_record (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date        TEXT,
    trade_time        TEXT,
    etf_code          TEXT,
    etf_name          TEXT,
    trade_type        TEXT,
    quantity          INTEGER,
    price             REAL,
    amount            REAL,
    fee               REAL,
    tax               REAL,
    settlement_amount REAL
);

-- ============================================================================
-- 表名: ods_market_price
-- 用途: 存储ETF实时行情快照
-- 字段说明:
--   etf_code:      ETF代码 (主键)
--   etf_name:      ETF名称
--   fund_type:     基金类型
--   current_price: 当前价格
--   update_time:   更新时间
-- ============================================================================

DROP TABLE IF EXISTS ods_market_price;

CREATE TABLE ods_market_price (
    etf_code      TEXT PRIMARY KEY,
    etf_name      TEXT,
    fund_type     TEXT,
    current_price REAL,
    update_time   TEXT
);

-- ============================================================================
-- 表名: ods_market_kline
-- 用途: 存储ETF日K线历史数据
-- 字段说明:
--   id:          自增主键
--   etf_code:    ETF代码
--   etf_name:    ETF名称
--   trade_date:  交易日期
--   open_price:  开盘价
--   high_price:  最高价
--   low_price:   最低价
--   close_price: 收盘价
--   volume:      成交量
--   amount:      成交额
--   update_time: 更新时间
-- ============================================================================

DROP TABLE IF EXISTS ods_market_kline;

CREATE TABLE ods_market_kline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    etf_code    TEXT NOT NULL,
    etf_name    TEXT,
    trade_date  TEXT NOT NULL,
    open_price  REAL,
    high_price  REAL,
    low_price   REAL,
    close_price REAL,
    volume      REAL,
    amount      REAL,
    update_time TEXT
);

CREATE INDEX IF NOT EXISTS idx_kline_code_date
    ON ods_market_kline (etf_code, trade_date);
