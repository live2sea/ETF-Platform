DROP TABLE IF EXISTS ods_trade_record;
--------------------------------------
-- 原始交易记录表
-- 该表用于存储从券商平台导出的ETF交易记录，包含交易的基本信息，如交易日期、时间、ETF代码、名称、交易类型、数量、价格、金额、费用、税费和结算金额等。
-- 该表的数据将作为后续数据处理和分析的基础，确保交易记录的完整性和准确性。
CREATE TABLE ods_trade_record(
--  唯一标识符，自动递增        
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT,

    trade_time TEXT,

    etf_code TEXT,

    etf_name TEXT,

    trade_type TEXT,

    quantity INTEGER,

    price REAL,

    amount REAL,

    fee REAL,

    tax REAL,

    settlement_amount REAL
);



DROP TABLE IF EXISTS dwd_profit_analysis;
--  =====================================
-- 盈亏分析表
-- 该表用于存储每只ETF的盈亏分析结果，包括ETF代码、名称、持仓数量、平均成本、已实现盈亏、盈亏排名和更新时间等字段。
-- 该表的数据将通过对当前持仓表和原始交易记录进行计算和分析得到，用于评估每只ETF的盈亏情况和排名，帮助投资者了解投资组合的表现。
CREATE TABLE dwd_profit_analysis(

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    quantity INTEGER,

    avg_cost REAL,

    realized_profit REAL,

    profit_rank INTEGER,

    update_time TEXT
);



-- ==========================================
-- 市场价格表
DROP TABLE IF EXISTS ods_market_price;

CREATE TABLE ods_market_price (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    fund_type TEXT,

    current_price REAL,

    update_time TEXT

);


--=========================================
-- 市场K线数据表    
DROP TABLE IF EXISTS ods_market_kline;

CREATE TABLE ods_market_kline (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    etf_code TEXT NOT NULL,

    etf_name TEXT,

    trade_date TEXT NOT NULL,

    open_price REAL,

    high_price REAL,

    low_price REAL,

    close_price REAL,

    volume REAL,

    amount REAL,

    update_time TEXT

);

CREATE INDEX idx_kline_code_date
ON ods_market_kline(etf_code, trade_date);

